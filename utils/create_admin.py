import os
import sys
from sqlalchemy import inspect

# Add root path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from app import create_app
from extensions import db
from models import AdminUser

# Load environment variables
load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# List of databases to process
DATABASES = [
    "instance/dev.db",
    "instance/ntkrv.db",
    "instance/test.db",
]

print("Starting admin creation process...")
print(f"Username: {ADMIN_USERNAME}\n")

for db_path in DATABASES:
    if not os.path.exists(db_path):
        print(f"Database not found, skipping: {db_path}")
        continue

    print(f"Using database: {db_path}")

    # Set database dynamically
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    with app.app_context():
        inspector = inspect(db.engine)

        # Check if table exists
        if not inspector.has_table("admin_user"):
            print("admin_user table missing — creating...")
            db.create_all()
        else:
            # Verify table columns
            columns = [col["name"] for col in inspector.get_columns("admin_user")]
            if not {"id", "username", "password_hash"}.issubset(columns):
                print("admin_user table has outdated structure — recreating...")
                db.drop_all()
                db.create_all()
            else:
                print("admin_user table structure OK")

        # Create or update admin
        existing_admin = AdminUser.query.filter_by(username=ADMIN_USERNAME).first()
        if existing_admin:
            print(f"Updating password for '{ADMIN_USERNAME}'...")
            existing_admin.set_password(ADMIN_PASSWORD)
        else:
            print(f"Creating new admin '{ADMIN_USERNAME}'...")
            new_admin = AdminUser(username=ADMIN_USERNAME)
            new_admin.set_password(ADMIN_PASSWORD)
            db.session.add(new_admin)

        db.session.commit()
        print(f"Admin verified successfully for {db_path}\n")

print("All databases processed successfully.")
