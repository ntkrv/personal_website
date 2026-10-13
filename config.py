import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Hard cap on uploaded body size (covers project image uploads).
    # 4 MB is plenty for case-study cover images.
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"

    # Number of reverse proxies in front of the app (Nginx, a load
    # balancer…). When > 0, ProxyFix trusts that many X-Forwarded-For /
    # X-Forwarded-Proto hops, so rate limits key on the real client IP
    # instead of the proxy's. Must match the real topology: too high and
    # clients can spoof their IP via the header.
    TRUSTED_PROXY_COUNT = int(os.getenv("TRUSTED_PROXY_COUNT", 0))

    # Rate-limit counters. memory:// is per-process, so with several
    # Gunicorn workers each one counts separately — use a shared backend
    # (e.g. redis://localhost:6379, needs the `redis` package) in prod.
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    # Where admin-uploaded case-study images are stored. Defaults to
    # instance/uploads/projects/ (outside the code checkout).
    UPLOAD_DIR = os.getenv("UPLOAD_DIR")

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///instance/ntkrv.db"
    )
    DEBUG = False
    ENV = "production"
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 31536000
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"

    # Production runs behind Nginx (see README → Deployment).
    TRUSTED_PROXY_COUNT = int(os.getenv("TRUSTED_PROXY_COUNT", 1))


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )
    SECRET_KEY = "testing-secret-key"
    WTF_CSRF_ENABLED = False
