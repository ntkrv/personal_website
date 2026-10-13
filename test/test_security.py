import pytest

from app import create_app
from config import TestingConfig
from extensions import db
from models import AdminUser
from utils.token_utils import generate_reset_token

NEW_PASSWORD = "a-long-new-password"


@pytest.fixture
def admin(app):
    user = AdminUser(username="admin")
    user.set_password("old-password-123")
    db.session.add(user)
    db.session.commit()
    return user


def _reset(client, token, password=NEW_PASSWORD, confirm=None):
    return client.post(
        f"/admin-auth/reset-password/{token}",
        data={"new_password": password, "confirm_password": confirm or password},
    )


def test_reset_token_is_single_use(client, admin):
    token = generate_reset_token(admin)

    first = _reset(client, token)
    assert first.status_code == 302
    assert first.headers["Location"].endswith("/admin-auth/login")

    second = _reset(client, token, password="another-long-password")
    assert second.headers["Location"].endswith("/admin-auth/forgot-password")
    assert db.session.get(AdminUser, admin.id).check_password(NEW_PASSWORD)


def test_reset_token_dies_when_password_changes_elsewhere(client, admin):
    token = generate_reset_token(admin)
    admin.set_password("changed-via-cli-123")
    db.session.commit()

    response = _reset(client, token)
    assert response.headers["Location"].endswith("/admin-auth/forgot-password")


def test_reset_token_rejects_garbage(client, admin):
    response = _reset(client, "not-a-token")
    assert response.headers["Location"].endswith("/admin-auth/forgot-password")


def test_reset_rejects_short_password(client, admin):
    token = generate_reset_token(admin)

    response = _reset(client, token, password="short")
    assert response.status_code == 200
    assert b"Use 12 to 128 characters." in response.data
    assert db.session.get(AdminUser, admin.id).check_password("old-password-123")


class ProxiedConfig(TestingConfig):
    TRUSTED_PROXY_COUNT = 1


def test_rate_limit_keys_on_forwarded_client_ip():
    app = create_app(ProxiedConfig)
    client = app.test_client()

    def login_from(ip):
        return client.post(
            "/admin-auth/login",
            data={"username": "x", "password": "y"},
            headers={"X-Forwarded-For": ip},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )

    with app.app_context():
        db.create_all()
        statuses = [login_from("203.0.113.1").status_code for _ in range(6)]
        assert statuses[-1] == 429
        # Same proxy, different client: not throttled by the first one.
        assert login_from("203.0.113.2").status_code != 429
        db.drop_all()
