from models import Project, Certificate, ContactMessage, AdminUser
from datetime import datetime


def test_project_model(app):
    project = Project(
        title="Test Project",
        short_description="Short desc",
        long_description="Long desc",
        image_path="image.png",
        skills="Python, Flask",
        git_link="https://github.com/test",
    )

    with app.app_context():
        from extensions import db

        db.session.add(project)
        db.session.commit()

        assert Project.query.count() == 1
        assert Project.query.first().title == "Test Project"


def test_certificate_model(app):
    cert = Certificate(
        title="Flask Certificate", issuer="Coursera", link="https://example.com/cert"
    )

    with app.app_context():
        from extensions import db

        db.session.add(cert)
        db.session.commit()

        saved = Certificate.query.first()
        assert saved.issuer == "Coursera"


def test_contact_message_model(app):
    msg = ContactMessage(name="Alice", email="alice@example.com", message="Hello!")

    with app.app_context():
        from extensions import db

        db.session.add(msg)
        db.session.commit()

        saved = ContactMessage.query.first()
        assert saved.name == "Alice"
        assert isinstance(saved.created_at, datetime)


def test_admin_user_password_hashing(app):
    user = AdminUser(username="admin")
    user.set_password("secure123")

    with app.app_context():
        from extensions import db

        db.session.add(user)
        db.session.commit()

        saved = AdminUser.query.first()
        assert saved.check_password("secure123") is True
        assert saved.check_password("wrong") is False
