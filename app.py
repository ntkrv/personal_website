import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from extensions import db, mail, migrate, login_manager, limiter, talisman
from flask_admin import Admin
from admin_panel import MyAdminIndexView, SecureModelView
from models import Project, Certificate, ContactMessage, AdminUser
from routes.main import main_bp
from routes.projects import projects_bp
from routes.certificates import certificates_bp
from routes.contact import contact_bp
from routes.admin_auth import admin_auth_bp
from routes.admin_manage import admin_manage_bp

load_dotenv()

csp = {
    "default-src": "'self'",
    "style-src": ["'self'", "https://fonts.googleapis.com"],
    "font-src": ["'self'", "https://fonts.gstatic.com"],
    "script-src": ["'self'"],
}


def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=True)

    if config_class:
        app.config.from_object(config_class)
    else:
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

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    talisman.init_app(app, content_security_policy=csp)

    login_manager.login_view = "admin_auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify(error="Too many requests. Please try again later."), 429

    @app.before_request
    def log_ip():
        if request.endpoint == "contact.contact":
            ip = request.remote_addr
            app.logger.info(f"Contact form accessed by IP: {ip}")

    admin = Admin(
        name="Admin Panel",
        url="/admin",
        template_mode="bootstrap4",
        index_view=MyAdminIndexView(),
    )
    admin.init_app(app)

    admin.add_view(SecureModelView(Project, db.session))
    admin.add_view(SecureModelView(Certificate, db.session))
    admin.add_view(SecureModelView(ContactMessage, db.session))

    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(certificates_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(admin_manage_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run()
