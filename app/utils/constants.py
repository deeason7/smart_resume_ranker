# app/utils/constants.py
"""
Stores application-wide constants to be used by various services and utilities.
"""
SECTION_HEADINGS = {
    "SUMMARY": [r"summary", r"profile", r"objective", r"about me"],
    "EXPERIENCE": [r"experience", r"work history", r"employment history", r"professional experience", r"career summary"],
    "SKILLS": [r"skills", r"technical skills", r"core competencies", r"technologies", r"proficiencies"],
    "EDUCATION": [r"education", r"academic background", r"qualifications", r"certifications"],
    # Sections specific to job descriptions
    "RESPONSIBILITIES": [r"responsibilities", r"duties", r"what you'll do", r"key responsibilities"],
}

CORE_SKILLS_LIST = [
    "python", "java", "c++", "c#", "javascript", "typescript", "ruby", "go", "rust", "swift", "kotlin",
    "sql", "nosql", "postgresql", "mysql", "mongodb", "redis",
    "react", "angular", "vue.js", "next.js", "node.js", "django", "flask", "ruby on rails",
    "html", "css", "sass",
    "aws", "azure", "google cloud", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "keras",
    "pandas", "numpy", "matplotlib", "seaborn",
    "tableau", "power bi", "looker", "dbt",
    "data analysis", "data science", "data engineering", "etl", "data warehousing",
    "agile", "scrum", "jira"
]