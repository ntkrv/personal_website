from models import Project, Certificate
from services.project_service import (
    create_project,
    update_project,
    delete_project,
)
from services.certificate_service import (
    create_certificate,
    update_certificate,
    delete_certificate,
)


def test_create_project_persists_and_generates_slug(app):
    with app.app_context():
        project = create_project(
            {
                "title": "My Cool Project",
                "short_description": "Short",
                "long_description": "Long",
                "image_path": "img.png",
                "stack": "Python",
                "link_type": "github",
                "git_link": "https://github.com/x/y",
            }
        )
        assert project.id is not None
        assert project.slug == "my-cool-project"
        assert Project.query.count() == 1


def test_create_project_ignores_unknown_fields(app):
    with app.app_context():
        project = create_project(
            {"title": "T", "short_description": "S", "long_description": "L",
             "stack": "Py", "link_type": "github", "git_link": "https://x.io",
             "evil_field": "drop tables"}
        )
        assert not hasattr(project, "evil_field") or project.evil_field is None


def test_update_project_changes_fields(app):
    with app.app_context():
        project = create_project(
            {"title": "Initial", "short_description": "s", "long_description": "l",
             "stack": "Py", "link_type": "github", "git_link": "https://x.io"}
        )
        update_project(project, {"title": "Updated", "stack": "Go"})
        refreshed = Project.query.first()
        assert refreshed.title == "Updated"
        assert refreshed.stack == "Go"


def test_delete_project_removes_row(app):
    with app.app_context():
        project = create_project(
            {"title": "ToDelete", "short_description": "s", "long_description": "l",
             "stack": "Py", "link_type": "github", "git_link": "https://x.io"}
        )
        delete_project(project)
        assert Project.query.count() == 0


def test_create_certificate_persists_skills(app):
    with app.app_context():
        cert = create_certificate(
            {
                "title": "Flask",
                "issuer": "Coursera",
                "skills": "Python, Flask",
                "link": "https://example.com",
            }
        )
        assert cert.id is not None
        assert cert.skills == "Python, Flask"


def test_update_certificate(app):
    with app.app_context():
        cert = create_certificate(
            {"title": "Old", "issuer": "X", "skills": "a", "link": "https://x.io"}
        )
        update_certificate(cert, {"title": "New", "skills": "b"})
        refreshed = Certificate.query.first()
        assert refreshed.title == "New"
        assert refreshed.skills == "b"


def test_delete_certificate(app):
    with app.app_context():
        cert = create_certificate(
            {"title": "X", "issuer": "Y", "skills": "z", "link": "https://x.io"}
        )
        delete_certificate(cert)
        assert Certificate.query.count() == 0
