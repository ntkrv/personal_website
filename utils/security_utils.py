from flask import current_app
from itsdangerous import URLSafeTimedSerializer


def generate_token(data: str, salt: str = "default") -> str:
    """
    Generate a secure token for the given data.

    Args:
        data (str): The data to encode.
        salt (str): Salt string to namespace the token.

    Returns:
        str: Encrypted token string.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(data, salt=salt)


def verify_token(token: str, salt: str = "default", max_age: int = 3600) -> str | None:
    """
    Verify a token and decode the original data.

    Args:
        token (str): The encrypted token.
        salt (str): Salt used during generation.
        max_age (int): Maximum age in seconds for token validity.

    Returns:
        str or None: Decoded data if valid, None otherwise.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return serializer.loads(token, salt=salt, max_age=max_age)
    except Exception:
        return None
