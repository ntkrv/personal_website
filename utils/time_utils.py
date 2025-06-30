from datetime import datetime

def format_datetime(dt: datetime) -> str:
    """
    Format a datetime object for display.

    Args:
        dt (datetime): A datetime object.

    Returns:
        str: Formatted date string.
    """
    return dt.strftime("%d.%m.%Y %H:%M") if dt else ""

def current_timestamp() -> datetime:
    """
    Get the current UTC timestamp.

    Returns:
        datetime: Current UTC time.
    """
    return datetime.utcnow()