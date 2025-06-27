import pytest
from app import app as flask_app
from models import db
from config import TestingConfig


@pytest.fixture
def app():
    flask_app.config.from_object(TestingConfig)

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
