# app/services/nlp_service.py
import spacy
import re
from spacy.matcher import PhraseMatcher
from datetime import datetime
import os
import json
import textstat

# Document section headings, used for parsing resumes and job descriptions.
SECTION_HEADINGS = {
    "SUMMARY": [r"summary", r"profile", r"objective", r"about me"],
    "EXPERIENCE": [r"experience", r"work history", r"employment history", r"professional experience",
                   r"career summary"],
    "SKILLS": [r"skills", "technical skills", r"core competencies", r"technologies", r"proficiencies"],
    "EDUCATION": [r"education", r"academic background", r"qualifications", r"certifications"],
    "RESPONSIBILITIES": [r"responsibilities", r"duties", r"what you'll do", r"key responsibilities"],
}

class NLPService:
    """A service for advanced NLP processing of text documents."""
    def __init__(self):
        """Loads the spaCy model and initializes the skill matcher."""
        self.nlp = self._load_spacy_model()
        self.skill_patterns = self._load_skill_patterns()
        self.matcher = PhraseMatcher(self.nlp.vocab, attr='LOWER')
        if self.skill_patterns:
            self.matcher.add("SKILL", self.skill_patterns)

    @staticmethod
    def _load_spacy_model():
        """
        Loads the spaCy model, downloading it if necessary.
        """
        try:
            return spacy.load("en_core_web_md")
        except OSError:
            print("Downloading 'en_core_web_md' model...")
            spacy.cli.download("en_core_web_md")
            return spacy.load("en_core_web_md")

    def _load_skill_patterns(self) -> list:
        """Loads skill patterns dynamically from an external JSON file."""
        skills_path = ""
        try:
            current_dir = os.path.dirname(__file__)
            skills_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'skills.json'))
            with open(skills_path, 'r', encoding='utf-8') as f:
                skills_data = json.load(f)

            all_skills = [skill for category in skills_data.values() for skill in category]
            print(f"INFO: Loaded {len(all_skills)} skills from skills.json")
            # Use the instance's nlp model to create spaCy doc patterns.
            return [self.nlp.make_doc(text) for text in all_skills]

        except FileNotFoundError:
            print(f"FATAL: skills.json not found at {skills_path}. No skills will be matched.")
            return []
        except json.JSONDecodeError:
            print(f"FATAL: Could not decode skills.json. Please check syntax.")
            return []

    def _extract_skills(self, doc: spacy.tokens.Doc) -> list:
        """Extracts skills using the pre-built matcher."""
        matches = self.matcher(doc)
        skills = {doc[start:end].text.lower() for _, start, end in matches}
        return sorted(list(skills))

    @staticmethod
    def _extract_stylistic_features(text: str) -> dict:
        """Calculates stylistic metrics like readability."""
        if not text or len(text.split()) < 100:
            return {"readability_score": 0, "readability_level": "N/A"}

        # Calculate score based on the input 'text', not an undefined variable.
        readability_score = textstat.flesch_reading_ease(text)

        if readability_score > 90:
            level = "Very Easy"
        elif readability_score > 70:
            level = "Easy"
        elif readability_score > 50:
            level = "Standard"
        elif readability_score > 30:
            level = "Difficult"
        else:
            level = "Very Difficult"

        return {
            "readability_score": round(readability_score, 2),
            "readability_level": level
        }

    @staticmethod
    def _extract_behavioral_metrics(text: str) -> dict:
        """Finds and counts unique action verbs to score accomplishments."""
        action_verbs = [
            'achieved', 'analyzed', 'authored', 'automated', 'budgeted', 'built',
            'created', 'decreased', 'delivered', 'designed', 'developed', 'directed',
            'enhanced', 'established', 'executed', 'generated', 'implemented',
            'improved', 'increased', 'initiated', 'innovated', 'launched', 'led',
            'managed', 'mentored', 'negotiated', 'optimized', 'orchestrated',
            'organized', 'oversaw', 'pioneered', 'planned', 'produced',
            'recommended', 'redesigned', 'reduced', 'researched', 'resolved',
            'restored', 'saved', 'slashed', 'solved', 'spearheaded', 'streamlined',
            'supervised', 'trained', 'transformed', 'won'
        ]

        found = re.findall(r'\b(' + '|'.join(action_verbs) + r')\b', text, re.IGNORECASE)
        accomplishment_score = len(set(v.lower() for v in found))
        return {"accomplishment_score": accomplishment_score}

    @staticmethod
    def _extract_experience_years(text: str) -> int:
        """Calculates total years of experience by parsing date ranges."""
        date_range_regex = r'\b(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+)?(\d{4})\b\s*-\s*\b(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present)\s+)?(\d{4}|Present)\b'
        matches = re.findall(date_range_regex, text, re.IGNORECASE)
        total_months = 0
        now = datetime.now()

        for start_m, start_y, end_m, end_y in matches:
            start_year = int(start_y)
            start_month = datetime.strptime(start_m, '%b').month if start_m else 1

            if 'present' in end_y.lower():
                end_year, end_month = now.year, now.month
            else:
                end_year = int(end_y)
                end_month = datetime.strptime(end_m, '%b').month if end_m else 12

            duration = (end_year - start_year) * 12 + (end_month - start_month) + 1
            if duration > 0:
                total_months += duration

        return total_months // 12

    @staticmethod
    def _extract_education_level(text: str) -> str:
        """Extracts the highest education level found in the text."""
        text_lower = text.lower()
        if any(edu in text_lower for edu in ["ph.d", "phd", "doctor of philosophy"]):
            return "Doctorate"
        if any(edu in text_lower for edu in ["master", "m.s", "m.sc", "m.eng", "mba"]):
            return "Master's Degree"
        if any(edu in text_lower for edu in ["bachelor", "b.s", "b.sc", "b.a."]):
            return "Bachelor's Degree"
        if any(edu in text_lower for edu in ["associate", "a.s", "a.a"]):
            return "Associate Degree"
        return "Not Found"

    def process_document(self, text: str) -> dict:
        """Performs a full analysis of a document, orchestrating all sub-tasks."""
        if not text:
            return {}

        doc = self.nlp(text)

        # Sectionizing Logic
        current_section = "HEADER"
        sections = {key: [] for key in SECTION_HEADINGS.keys()}
        sections.update({"HEADER": [], "OTHER": []})
        for line in text.split('\n'):
            line = line.strip()
            if not line: continue
            matched_section = next(
                (name for name, patterns in SECTION_HEADINGS.items() if any(re.match(p, line, re.I) for p in patterns)),
                None)
            if matched_section:
                current_section = matched_section
            else:
                sections.get(current_section, sections["OTHER"]).append(line)
        raw_sections = {name: "\n".join(lines) for name, lines in sections.items()}

        # Feature Extraction
        processed_data = {
            "skills": ", ".join(self._extract_skills(doc)),
            "experience_years": self._extract_experience_years(text),
            "education_level": self._extract_education_level(text),
            "raw_sections": raw_sections
        }

        processed_data.update(self._extract_stylistic_features(text))
        processed_data.update(self._extract_behavioral_metrics(text))

        return processed_data