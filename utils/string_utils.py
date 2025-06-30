import re
import unicodedata
from markupsafe import escape

def sanitize_input(text: str) -> str:
    """
    Sanitize user input by trimming and escaping HTML.

    Args:
        text (str): Raw user input.

    Returns:
        str: Safe, escaped string.
    """
    return escape(text.strip())

def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    """
    Check if uploaded file has a valid extension.

    Args:
        filename (str): Name of the uploaded file.
        allowed_extensions (set): Allowed file extensions.

    Returns:
        bool: True if valid, else False.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def slugify(text: str) -> str:
    """
    Generate a URL-friendly slug from a string.

    Args:
        text (str): Input text (e.g. project title).

    Returns:
        str: Slugified version of the string.
    """
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)