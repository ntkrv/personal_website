import hashlib
import hmac

from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from models import AdminUser

SALT = "password-reset-salt"


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


# The token carries a fingerprint of the current password hash, so it
# stops verifying the moment the password changes: every reset link is
# single-use, and older links die with it. The fingerprint is a digest
# rather than a slice of the hash itself — token payloads are signed,
# not encrypted, and must not leak hash material.
def _password_fingerprint(user: AdminUser) -> str:
    return hashlib.sha256(user.password_hash.encode()).hexdigest()[:32]


def generate_reset_token(user: AdminUser) -> str:
    return _serializer().dumps(
        {"u": user.username, "p": _password_fingerprint(user)}, salt=SALT
    )


def verify_reset_token(token: str, expiration: int = 3600) -> AdminUser | None:
    try:
        data = _serializer().loads(token, salt=SALT, max_age=expiration)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None

    user = AdminUser.query.filter_by(username=data.get("u")).first()
    if user is None:
        return None
    if not hmac.compare_digest(str(data.get("p", "")), _password_fingerprint(user)):
        return None
    return user
