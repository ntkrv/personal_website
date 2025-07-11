import os
from dotenv import load_dotenv

from app import create_app
from extensions import db
from models import AdminUser

load_dotenv()

app = create_app()

with app.app_context():
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")

    if not username or not password:
        raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD must be set in .env")

    admin = AdminUser.query.filter_by(username=username).first()
    if not admin:
        admin = AdminUser(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created.")
    else:
        print("ℹ️ Admin user already exists.")
