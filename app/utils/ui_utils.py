# app/utils/ui_utils.py
"""
This module contains utility functions specifically for enhancing the user interface (UI).
"""
import re
from markupsafe import Markup

def highlight_keywords(text: str, keywords_str: str) -> Markup:
    if not keywords_str or not text:
        return text

    # Sanitize the input by stripping whitespace from each keyword
    keyword_list = [k.strip() for k in keywords_str.split(',') if k.strip()]
    if not keyword_list:
        return text

    regex = re.compile(
        r'\b(' + '|'.join(map(re.escape, keyword_list)) + r')\b',
        re.IGNORECASE
    )

    highlighted_text = regex.sub(r'<mark>\1</mark>', text)

    return Markup(highlighted_text)