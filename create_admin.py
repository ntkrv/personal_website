import os
from dotenv import load_dotenv
from app import app, db
from models import AdminUser

load_dotenv()

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")

with app.app_context():
    # Drop all prev accounts
    print("Deleting all existing admin users...")
    AdminUser.query.delete()
    db.session.commit()
    print("All existing admin users deleted.")

    # Create new admin
    print(f"Creating admin user '{username}'...")
    admin = AdminUser(username=username)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user '{username}' created successfully.")
