# app/utils/ui_utils.py
"""
This module contains utility functions specifically for enhancing the user interface (UI).
These functions are often registered as custom template filters in Jinja2.
"""
import re
from markupsafe import Markup

def highlight_keywords(text: str, keywords_str: str) -> Markup:
    """
    A Jinja2 filter that finds keywords within a block of text and wraps them
    in <mark> HTML tags for highlighting.

    Args:
        text: The source text to search within.
        keywords_str: A single string containing keywords separated by commas.

    Returns:
        A Markup object containing the text with HTML highlights, which is
        rendered safely by Jinja2.
    """
    if not keywords_str or not text:
        return text

    # Sanitize the input by stripping whitespace from each keyword
    keyword_list = [k.strip() for k in keywords_str.split(',') if k.strip()]
    if not keyword_list:
        return text

    # Regex pattern.
    # - `re.escape` handles cases where a keyword contains special regex characters (e.g., C++).
    # - `\b` creates word boundaries to prevent matching substrings (e.g., 'py' in 'python').
    # - `|` acts as an OR, so it finds any of the keywords.
    # - `re.IGNORECASE` makes the search case-insensitive.
    regex = re.compile(
        r'\b(' + '|'.join(map(re.escape, keyword_list)) + r')\b',
        re.IGNORECASE
    )

    # Use the regex's sub() method to find all occurrences and replace them.
    # The `\1` in the replacement refers to the actual matched keyword, preserving its original casing.
    highlighted_text = regex.sub(r'<mark>\1</mark>', text)

    # Return as a Markup object to prevent auto-escaping of the <mark> tags by Jinja2.
    return Markup(highlighted_text)