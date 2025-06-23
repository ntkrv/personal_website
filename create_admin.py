import os
from dotenv import load_dotenv
from app import app, db
from models import AdminUser

load_dotenv()

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")

with app.app_context():
    if AdminUser.query.filter_by(username=username).first():
        print(f"Admin user '{username}' already exists.")
    else:
        admin = AdminUser(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully.")