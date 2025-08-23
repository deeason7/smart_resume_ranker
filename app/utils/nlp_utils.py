# app/utils/nlp_utils.py
"""
This module contains utility functions for backend NLP-related tasks,
such as text cleaning and content extraction from files.
"""
import re
import docx
from PyPDF2 import PdfReader

def preprocess_text(text: str) -> str:
    """Cleans raw text for database storage or NLP processing.
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_text_from_file(file_path: str, filename: str) -> str:
    """Extracts raw text from an uploaded file (PDF or DOCX).
    """
    text = ""
    try:
        if filename.lower().endswith('.pdf'):
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        elif filename.lower().endswith('.docx'):
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        print(f"ERROR: Could not process file {filename}. Reason: {e}")
        return ""
    return text