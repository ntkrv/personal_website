import os
import pytest
from dotenv import load_dotenv

from app import create_app
from extensions import db
from models import AdminUser

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin-password-test")


@pytest.fixture
def client():
    app = create_app("config.TestingConfig")
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()

            admin = AdminUser(username=ADMIN_USERNAME)
            admin.set_password(ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()

        yield client


def test_admin_login_success(client):
    response = client.post(
        "/admin-auth/login",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        follow_redirects=True,
    )

    assert b"Invalid username or password" not in response.data
    assert response.status_code == 200


def test_admin_login_failure(client):
    response = client.post(
        "/admin-auth/login",
        data={"username": ADMIN_USERNAME, "password": "wrongpassword"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    assert b"Admin Login" in response.data


def test_login_open_redirect_blocked(client):
    response = client.post(
        "/admin-auth/login?next=https://evil.example.com/phish",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        follow_redirects=False,
    )

    assert response.status_code in (301, 302)
    location = response.headers.get("Location", "")
    assert "evil.example.com" not in location
