from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # <-- NEW
from config import DevelopmentConfig
from flask_login import LoginManager
from flask_admin import Admin

from routes.main import main_bp
from routes.projects import projects_bp
from routes.certificates import certificates_bp
from routes.contact import contact_bp
from routes.admin_auth import admin_auth_bp

from models import db, Project, Certificate, ContactMessage, AdminUser
from admin_panel import MyAdminIndexView, SecureModelView

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(DevelopmentConfig)

# DB init
db.init_app(app)

# Migrate init
migrate = Migrate(app, db)  # <-- THIS LINE

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_auth.login"


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


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

# DB create (не нужен при использовании миграций, но не мешает)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
