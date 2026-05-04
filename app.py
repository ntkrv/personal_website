import os
import re
from datetime import datetime

from flask import Flask, request
from markupsafe import Markup, escape
from dotenv import load_dotenv

from extensions import db, mail, migrate, login_manager, limiter, talisman, csrf
from models import AdminUser
from utils.logging_config import configure_logging

load_dotenv()

CSP = {
    "default-src": "'self'",
    "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    "font-src": ["'self'", "https://fonts.gstatic.com"],
    "script-src": [
        "'self'",
        "'unsafe-inline'",
        "https://www.googletagmanager.com",
    ],
    "connect-src": [
        "'self'",
        "https://www.google-analytics.com",
        "https://*.analytics.google.com",
        "https://*.googletagmanager.com",
    ],
    "img-src": [
        "'self'",
        "data:",
        "https://images.unsplash.com",
        "https://www.google-analytics.com",
        "https://*.googletagmanager.com",
    ],
}

# Anchor for the auto-incrementing "Years in data" stat on the hero.
# years_in_data = current_year - CAREER_START_YEAR  →  rolls forward
# automatically each January 1.
CAREER_START_YEAR = 2021


def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=True)

    os.makedirs(app.instance_path, exist_ok=True)

    _load_config(app, config_class)
    _validate_config(app)
    configure_logging(app)
    _register_extensions(app)
    _register_blueprints(app)
    _register_request_hooks(app)
    _register_cli(app)

    return app


def _load_config(app, config_class) -> None:
    if config_class:
        app.config.from_object(config_class)
        return

    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        from config import ProductionConfig

        app.config.from_object(ProductionConfig)
    elif env == "testing":
        from config import TestingConfig

        app.config.from_object(TestingConfig)
    else:
        from config import DevelopmentConfig

        app.config.from_object(DevelopmentConfig)


def _validate_config(app) -> None:
    if not app.config.get("SECRET_KEY") and not app.config.get("TESTING"):
        raise RuntimeError("SECRET_KEY environment variable must be set.")


def _register_extensions(app) -> None:
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    force_https = (
        os.getenv("FLASK_ENV", "").lower() == "production"
        and not app.config.get("TESTING")
    )
    talisman.init_app(
        app,
        content_security_policy=CSP,
        force_https=force_https,
        session_cookie_secure=force_https,
    )

    login_manager.login_view = "admin_auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(AdminUser, int(user_id))


def _register_blueprints(app) -> None:
    from routes.main import main_bp
    from routes.projects import projects_bp
    from routes.certificates import certificates_bp
    from routes.contact import contact_bp
    from routes.agencies import agencies_bp
    from routes.admin_auth import admin_auth_bp
    from routes.admin_manage import admin_manage_bp
    from routes.errors import errors_bp
    from routes.demo import demo_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(certificates_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(agencies_bp)
    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(admin_manage_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(demo_bp)


def _register_request_hooks(app) -> None:
    @app.before_request
    def log_contact_access():
        if request.endpoint == "contact.contact":
            app.logger.info("Contact form accessed by IP: %s", request.remote_addr)

    @app.context_processor
    def inject_globals():
        year = datetime.now().year
        return {
            "current_year": year,
            "years_in_data": max(year - CAREER_START_YEAR, 1),
            "ga_measurement_id": os.getenv("GA_MEASUREMENT_ID", "").strip(),
            "privacy_contact_email": os.getenv(
                "PRIVACY_CONTACT_EMAIL", "contact@ntkrv.dev"
            ),
        }

    app.jinja_env.filters["case_format"] = _case_format


# Renders a case-study long_description (plain text with `**bold.**`
# section leads) into safe HTML: each blank-line-separated paragraph
# becomes a <p>, and a leading `**...**` chunk becomes an h3 eyebrow
# above the paragraph body. All non-marker content is escaped first,
# so admin input can't smuggle in HTML.
_BOLD_LEAD_RE = re.compile(r"^\s*\*\*(?P<heading>[^*]+?)\*\*\s*(?P<body>.*)", re.DOTALL)


def _case_format(value):
    if not value:
        return Markup("")

    blocks = []
    for raw in re.split(r"\n\s*\n", str(value).strip()):
        chunk = raw.strip()
        if not chunk:
            continue
        match = _BOLD_LEAD_RE.match(chunk)
        if match:
            heading = escape(match.group("heading").strip().rstrip("."))
            body = escape(match.group("body").strip()).replace("\n", "<br>")
            blocks.append(
                f'<div class="case-section">'
                f'<h3 class="case-heading">{heading}</h3>'
                f'<p class="case-body">{body}</p>'
                f"</div>"
            )
        else:
            body = escape(chunk).replace("\n", "<br>")
            blocks.append(f'<p class="case-body">{body}</p>')
    return Markup("".join(blocks))


def _register_cli(app) -> None:
    from cli import register_cli

    register_cli(app)


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run()
