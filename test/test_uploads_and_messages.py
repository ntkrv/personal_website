import io
import os

import pytest

from config import TestingConfig
from extensions import db, mail
from models import AdminUser, ContactMessage, Project
from utils.uploads import UPLOAD_URL_PREFIX, migrate_legacy_uploads

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64


@pytest.fixture
def app(tmp_path):
    from app import create_app

    class Config(TestingConfig):
        UPLOAD_DIR = str(tmp_path / "uploads")

    app = create_app(Config)
    app.static_folder = str(tmp_path / "static")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def admin_client(client):
    user = AdminUser(username="admin")
    user.set_password("admin-password-123")
    db.session.add(user)
    db.session.commit()
    client.post(
        "/admin-auth/login",
        data={"username": "admin", "password": "admin-password-123"},
    )
    return client


def _project_form(**extra):
    data = {
        "title": "Case",
        "short_description": "Short",
        "long_description": "Long",
        "link_type": "github",
    }
    data.update(extra)
    return data


def _upload(client, content, name="cover.png", url="/admin/project/add"):
    return client.post(
        url,
        data=_project_form(image_file=(io.BytesIO(content), name)),
        content_type="multipart/form-data",
    )


def _stored_file(app, project):
    name = project.image_path[len(UPLOAD_URL_PREFIX):]
    return os.path.join(app.config["UPLOAD_DIR"], name)


def test_upload_is_stored_outside_static_and_served(app, admin_client):
    assert _upload(admin_client, PNG).status_code == 302

    project = Project.query.one()
    assert project.image_path.startswith(UPLOAD_URL_PREFIX)
    assert project.image_path.endswith(".png")
    assert os.path.exists(_stored_file(app, project))

    response = admin_client.get(project.image_path)
    assert response.status_code == 200
    assert response.data == PNG


def test_upload_extension_comes_from_content(app, admin_client):
    _upload(admin_client, JPEG, name="cover.png")
    assert Project.query.one().image_path.endswith(".jpg")


def test_upload_rejects_non_image_content(app, admin_client):
    response = _upload(admin_client, b"<?php echo 1; ?>", name="shell.png")

    assert response.status_code == 200
    assert b"isn&#39;t a valid jpg, png, or webp image" in response.data
    assert Project.query.count() == 0


def test_replacing_image_deletes_old_file(app, admin_client):
    _upload(admin_client, PNG)
    project = Project.query.one()
    old_file = _stored_file(app, project)

    _upload(admin_client, JPEG, name="new.jpg", url=f"/admin/edit_project/{project.id}")

    assert not os.path.exists(old_file)
    assert os.path.exists(_stored_file(app, db.session.get(Project, project.id)))


def test_deleting_project_deletes_its_file(app, admin_client):
    _upload(admin_client, PNG)
    project = Project.query.one()
    stored = _stored_file(app, project)

    admin_client.post(f"/admin/delete_project/{project.id}")

    assert not os.path.exists(stored)


def test_shared_or_external_images_are_left_alone(app, admin_client):
    _upload(admin_client, PNG)
    first = Project.query.one()
    stored = _stored_file(app, first)
    db.session.add(Project(title="Twin", image_path=first.image_path))
    db.session.commit()

    admin_client.post(f"/admin/delete_project/{first.id}")
    assert os.path.exists(stored)  # still used by "Twin"


def test_migrate_legacy_uploads(app):
    legacy_dir = os.path.join(app.static_folder, "uploads", "projects")
    os.makedirs(legacy_dir)
    name = "a" * 32 + ".png"
    with open(os.path.join(legacy_dir, name), "wb") as f:
        f.write(PNG)
    db.session.add(Project(title="Old", image_path="/static/uploads/projects/" + name))
    db.session.add(Project(title="Gone", image_path="/static/uploads/projects/" + "b" * 32 + ".png"))
    db.session.commit()

    moved, missing = migrate_legacy_uploads()

    assert moved == 1 and len(missing) == 1
    assert Project.query.filter_by(title="Old").one().image_path == UPLOAD_URL_PREFIX + name
    assert os.path.exists(os.path.join(app.config["UPLOAD_DIR"], name))


def test_contact_message_shows_in_dashboard_and_can_be_deleted(app, admin_client):
    with mail.record_messages():
        admin_client.post(
            "/contact",
            data={"name": "Ann", "email": "ann@example.com", "message": "Hello <b>there</b>"},
        )
    message = ContactMessage.query.one()

    page = admin_client.get("/admin/dashboard").data
    assert b"ann@example.com" in page
    assert b"Hello &lt;b&gt;there&lt;/b&gt;" in page

    admin_client.post(f"/admin/delete_message/{message.id}")
    assert ContactMessage.query.count() == 0


def test_contact_smtp_failure_is_logged_not_raised(app, client, monkeypatch, caplog):
    monkeypatch.setenv("MAIL_DEFAULT_RECIPIENT", "owner@example.com")

    def boom(msg):
        raise ConnectionRefusedError("smtp down")

    monkeypatch.setattr(mail, "send", boom)
    from threading import Thread

    started = []
    monkeypatch.setattr(
        "utils.email_utils.Thread",
        lambda target, daemon: started.append(Thread(target=target)) or started[-1],
    )

    response = client.post(
        "/contact",
        data={"name": "Ann", "email": "ann@example.com", "message": "Hi"},
    )
    started[0].join()

    assert response.status_code == 302
    assert ContactMessage.query.count() == 1
    assert "Failed to send contact email" in caplog.text


def test_forgot_password_does_not_500_when_smtp_fails(app, client, monkeypatch):
    monkeypatch.setenv("ADMIN_RESET_EMAIL", "owner@example.com")
    user = AdminUser(username="admin")
    user.set_password("admin-password-123")
    db.session.add(user)
    db.session.commit()
    monkeypatch.setattr(mail, "send", lambda msg: (_ for _ in ()).throw(OSError("down")))

    matching = client.post("/admin-auth/forgot-password", data={"email": "owner@example.com"})
    other = client.post("/admin-auth/forgot-password", data={"email": "x@example.com"})

    assert matching.status_code == other.status_code == 302
    assert matching.headers["Location"] == other.headers["Location"]
