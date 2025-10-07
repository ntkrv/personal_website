import os
import sys
import shutil
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from models import Project, Certificate, AdminUser

source_uri = "sqlite:///instance/dev.db"
target_path = os.path.join("instance", "ntkrv.db")
target_uri = f"sqlite:///{target_path}"

app = create_app()

if os.path.exists(target_path):
    backup_name = f"ntkrv_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join("instance", backup_name)
    shutil.copy2(target_path, backup_path)
    print(f"Backup created: {backup_path}")
else:
    print("No existing ntkrv.db found — creating a new one.")


with app.app_context():
    app.config["SQLALCHEMY_DATABASE_URI"] = source_uri
    db.engine.dispose()
    db.reflect()
    projects = Project.query.all()
    certificates = Certificate.query.all()
    admins = AdminUser.query.all()

    print(f"\nExtracted {len(projects)} projects, {len(certificates)} certificates, {len(admins)} admins from dev.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = target_uri
    db.engine.dispose()
    db.reflect()

    for p in projects:
        db.session.merge(Project(**{c.name: getattr(p, c.name) for c in p.__table__.columns}))
    for c in certificates:
        db.session.merge(Certificate(**{f.name: getattr(c, f.name) for f in c.__table__.columns}))
    for a in admins:
        db.session.merge(AdminUser(**{f.name: getattr(a, f.name) for f in a.__table__.columns}))

    db.session.commit()
    print("\nData successfully migrated from dev.db → ntkrv.db")
