import os
import sys

# Add root project directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from app import create_app
from extensions import db
from models import AdminUser

# Load variables from .env
load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

app = create_app()

with app.app_context():
    existing_admin = AdminUser.query.filter_by(username=ADMIN_USERNAME).first()

    if existing_admin:
        print(f"Admin user '{ADMIN_USERNAME}' already exists. Updating password...")
        existing_admin.set_password(ADMIN_PASSWORD)
    else:
        print(f"👤 Creating new admin user: {ADMIN_USERNAME}")
        new_admin = AdminUser(username=ADMIN_USERNAME)
        new_admin.set_password(ADMIN_PASSWORD)
        db.session.add(new_admin)

    db.session.commit()
    print("Admin credentials saved.")
