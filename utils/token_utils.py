import os
from itsdangerous import URLSafeTimedSerializer


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))
    return serializer.dumps(email, salt="password-reset-salt")


def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=expiration)
    except Exception:
        return None
    return email
