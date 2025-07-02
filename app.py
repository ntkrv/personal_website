import os
from flask import Flask, jsonify, request, redirect
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

from routes.main import main_bp
from routes.projects import projects_bp
from routes.certificates import certificates_bp
from routes.contact import contact_bp
from routes.admin_auth import admin_auth_bp

from models import db, Project, Certificate, ContactMessage, AdminUser
from admin_panel import MyAdminIndexView, SecureModelView

# Load environment (for dev/prod switch)
from dotenv import load_dotenv

load_dotenv()

# App init
app = Flask(__name__, instance_relative_config=True)

# Dynamic config loader
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

# DB init
db.init_app(app)
migrate = Migrate(app, db)

# Security headers via Talisman
csp = {
    "default-src": "'self'",
    "style-src": ["'self'", "https://fonts.googleapis.com"],
    "font-src": ["'self'", "https://fonts.gstatic.com"],
    "script-src": ["'self'"],
}
Talisman(app, content_security_policy=csp)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_auth.login"


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


@app.route("/dashboard")
@app.route("/dashboard/")
def dashboard_redirect():
    return redirect("/admin", code=301)


@app.route("/dashboard/project/")
def dashboard_project_redirect():
    return redirect("/admin/project/", code=301)


@app.route("/dashboard/certificate/")
def dashboard_certificate_redirect():
    return redirect("/admin/certificate/", code=301)


# Flask-Limiter
limiter = Limiter(
    get_remote_address,
    storage_uri="redis://localhost:6379",
    app=app,
    default_limits=["100 per hour"],
)


# Rate limit exceeded
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Too many requests. Please try again later."), 429


# IP logger for contact form
@app.before_request
def log_ip():
    if request.endpoint == "contact.contact":
        ip = get_remote_address()
        app.logger.info(f"Contact form accessed by IP: {ip}")


# Flask-Admin
admin = Admin(
    app,
    name="Admin Panel",
    url="/admin",
    template_mode="bootstrap4",
    index_view=MyAdminIndexView(),
)

admin.add_view(SecureModelView(Project, db.session))
admin.add_view(SecureModelView(Certificate, db.session))
admin.add_view(SecureModelView(ContactMessage, db.session))

# Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(certificates_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(admin_auth_bp)

# Optional: create db if needed
with app.app_context():
    db.create_all()

# Run
if __name__ == "__main__":
    app.run()
