from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_limiter.util import get_remote_address

# from flask_mail import Mail

from routes.main import main_bp
from routes.projects import projects_bp
from routes.certificates import certificates_bp
from routes.contact import contact_bp
from routes.admin_auth import admin_auth_bp

from models import db, Project, Certificate, ContactMessage, AdminUser
from admin_panel import MyAdminIndexView, SecureModelView

# App init
app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config.ProductionConfig")

# DB
db.init_app(app)
migrate = Migrate(app, db)

# Security headers
SELF = "'self'"
GOOGLE_FONTS = "https://fonts.googleapis.com https://fonts.gstatic.com"
TAILWIND = "https://cdn.tailwindcss.com"


csp = {
    "default-src": "'self'",
    "style-src": ["'self'", "https://fonts.googleapis.com"],
    "font-src": ["'self'", "https://fonts.gstatic.com"],
    "script-src": ["'self'"],
}

Talisman(app, content_security_policy=csp)


# Flask-Mail
# app.config["MAIL_SERVER"] = "smtp.gmail.com"
# app.config["MAIL_PORT"] = 587
# app.config["MAIL_USE_TLS"] = True
# app.config["MAIL_USERNAME"] = "your_email@gmail.com"
# app.config["MAIL_PASSWORD"] = "your_app_password"
# app.config["MAIL_DEFAULT_SENDER"] = "your_email@gmail.com"
# mail = Mail(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_auth.login"


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


# Flask-Limiter
limiter = Limiter(
    get_remote_address,
    storage_uri="redis://localhost:6379",
    app=app,
    default_limits=["100 per hour"],
)


# Rate limit exceeded handler
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Too many requests. Please try again later."), 429


# IP logger
@app.before_request
def log_ip():
    if request.endpoint == "contact.contact":
        ip = get_remote_address()
        app.logger.info(f"Contact form accessed by IP: {ip}")


# Flask-Admin
admin = Admin(
    app, name="Admin Panel", template_mode="bootstrap4", index_view=MyAdminIndexView()
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

# Optional: Create DB (not required with migrations)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
