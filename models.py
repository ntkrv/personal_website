from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
from sqlalchemy import event
from extensions import db


# --- PROJECT MODEL ---
class Project(db.Model):
    __tablename__ = "project"
    __table_args__ = (db.UniqueConstraint("slug", name="uq_project_slug"),)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(160), nullable=False, index=True)
    short_description = db.Column(db.String(300))
    long_description = db.Column(db.Text)
    image_path = db.Column(db.String(120))
    stack = db.Column(db.String(200))
    link_type = db.Column(db.String(20))  # "github" or "gdrive"
    git_link = db.Column(db.String(255))

    def _make_unique_slug(self, base=None):
        base = base or slugify(self.title or "")
        candidate = base or "project"
        n = 2

        while Project.query.filter(
            Project.slug == candidate, Project.id != self.id
        ).first():
            candidate = f"{base}-{n}"
            n += 1

        self.slug = candidate


@event.listens_for(Project, "before_insert")
def _project_before_insert(mapper, connection, target: Project):
    if not target.slug:
        target._make_unique_slug()


@event.listens_for(Project, "before_update")
def _project_before_update(mapper, connection, target: Project):
    if not target.slug:
        target._make_unique_slug()


# --- CERTIFICATE MODEL ---
class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    issuer = db.Column(db.String(100))
    skills = db.Column(db.String(200))
    link = db.Column(db.String(255))


# --- CONTACT MESSAGE MODEL ---
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --- ADMIN USER MODEL ---
class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
