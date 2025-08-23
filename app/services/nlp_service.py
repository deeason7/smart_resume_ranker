# app/services/nlp_service.py
import spacy
import re
from spacy.matcher import PhraseMatcher
from datetime import datetime
from app.utils.constants import SECTION_HEADINGS, CORE_SKILLS_LIST


class NLPService:
    """
    A professional-grade service for advanced NLP processing of text documents.
    """

    def __init__(self):
        """Loads the spaCy model and initializes the skill matcher upon creation."""
        try:
            self.nlp = spacy.load("en_core_web_md")
        except OSError:
            print("Downloading 'en_core_web_md' model... This may take a moment.")
            spacy.cli.download("en_core_web_md")
            self.nlp = spacy.load("en_core_web_md")

        self.skill_patterns = [self.nlp.make_doc(text) for text in CORE_SKILLS_LIST]
        self.matcher = PhraseMatcher(self.nlp.vocab, attr='LOWER')
        self.matcher.add("SKILL", self.skill_patterns)

    def _extract_skills(self, doc: spacy.tokens.Doc) -> list:
        """Private helper to extract skills using our pre-built matcher."""
        matches = self.matcher(doc)
        skills = set(doc[start:end].text.lower() for match_id, start, end in matches)
        return sorted(list(skills))

    @staticmethod
    def _extract_experience_years(text: str) -> int:
        """
        Private helper to calculate total years of experience by parsing date ranges.
        """
        # This regex is designed to find year-based date ranges.
        date_range_regex = r'\b(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+)?(\d{4})\b\s*-\s*\b(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present)\s+)?(\d{4}|Present)\b'
        matches = re.findall(date_range_regex, text, re.IGNORECASE)

        total_months = 0
        current_year = datetime.now().year
        current_month = datetime.now().month

        for start_m, start_y, end_m, end_y in matches:
            start_year = int(start_y)
            start_month = datetime.strptime(start_m, '%b').month if start_m else 1

            if 'present' in end_y.lower():
                end_year = current_year
                end_month = current_month
            else:
                end_year = int(end_y)
                end_month = datetime.strptime(end_m, '%b').month if end_m else 12

            # Calculate the duration of each role in months and add to the total.
            duration = (end_year - start_year) * 12 + (end_month - start_month) + 1
            if duration > 0:
                total_months += duration

        return total_months // 12

    @staticmethod
    def _extract_education_level(text: str) -> str:
        """Private helper to extract the highest education level found."""
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
        """
        The main public method to perform a full analysis of a document.
        """
        if not text:
            return {}

        doc = self.nlp(text)

        # Sectionize the document
        current_section = "HEADER"
        sections = {key: [] for key in SECTION_HEADINGS.keys()}
        sections.update({"HEADER": [], "OTHER": []})

        for line in text.split('\n'):
            line = line.strip()
            if not line: continue

            matched_section = False
            for section_name, patterns in SECTION_HEADINGS.items():
                if any(re.match(p, line[:30], re.I) for p in patterns):
                    current_section = section_name
                    matched_section = True
                    break

            if not matched_section:
                sections.get(current_section, sections["OTHER"]).append(line)

        # Join lines for each section
        raw_sections = {name: "\n".join(lines) for name, lines in sections.items()}

        # Extract specific entities from the full text
        skills = self._extract_skills(doc)
        experience_years = NLPService._extract_experience_years(text)
        education_level = NLPService._extract_education_level(text)

        # Return a single, comprehensive dictionary
        return {
            "skills": ", ".join(skills),
            "experience_years": experience_years,
            "education_level": education_level,
            "raw_sections": raw_sections
        }