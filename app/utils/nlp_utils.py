# app/utils/nlp_utils.py
"""
This utility module provides core NLP and file processing functions.
It includes functions for:
- Extracting raw text from various file formats (PDF, DOCX).
- Performing basic text cleaning and preprocessing (lemmatization, stopword removal).
"""
import nltk
import string
import fitz  # PyMuPDF
import docx  # python-docx
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


# --- Professional NLTK Resource Management ---
def _ensure_nltk_resource(resource_path: str, resource_name: str):
    """
    A helper function to check for an NLTK resource and download it if missing.
    This prevents repetitive try/except blocks.
    """
    try:
        nltk.data.find(resource_path)
    except LookupError:
        print(f"Downloading NLTK resource: '{resource_name}'...")
        nltk.download(resource_name, quiet=True)


# Ensure all necessary NLTK packages are available on startup.
_ensure_nltk_resource('corpora/stopwords', 'stopwords')
_ensure_nltk_resource('tokenizers/punkt', 'punkt')
_ensure_nltk_resource('corpora/wordnet', 'wordnet')

# Initialize resources for use in functions
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


def preprocess_text(text: str) -> str:
    """
    Performs a standard NLP preprocessing pipeline on a string of text.

    The pipeline includes:
    1. Conversion to lowercase.
    2. Tokenization (splitting text into words).
    3. Removal of stopwords (common words like 'the', 'is', etc.).
    4. Removal of punctuation.
    5. Lemmatization (reducing words to their dictionary form, e.g., 'running' -> 'run').
    """
    if not isinstance(text, str):
        return ""

    # 1. Convert to lowercase for case-insensitive processing.
    text = text.lower()

    # 2. Tokenize text into a list of words.
    tokens = word_tokenize(text)

    # 3. & 4. & 5. Filter out stopwords/punctuation, keep only alphabetic tokens, and lemmatize.
    cleaned_tokens = [
        lemmatizer.lemmatize(token) for token in tokens
        if token.isalpha() and token not in stop_words and token not in string.punctuation
    ]

    return " ".join(cleaned_tokens)


# --- File Text Extraction ---

def extract_text_from_pdf(file_path: str) -> str | None:
    """Extracts all text content from a PDF file."""
    try:
        with fitz.open(file_path) as doc:
            return "".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return None


def extract_text_from_docx(file_path: str) -> str | None:
    """Extracts all text content from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return None


def extract_text_from_file(file_path: str, filename: str) -> str | None:
    """A generic file handler that routes to the correct text extractor based on file extension."""
    extension = filename.lower().rsplit('.', 1)[-1]
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    if extension == 'docx':
        return extract_text_from_docx(file_path)
    if extension == 'txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT {file_path}: {e}")
            return None
    return None  # Return None for unsupported file types