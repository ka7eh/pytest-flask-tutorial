import os
import tempfile

from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
import pytest

from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    """
    Return a Flask app instance.
    """
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({"TESTING": True, "DATABASE": db_path,})

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    print("Tearing Down App")

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """
    Return a Flask test client.
    """
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    """
    Return a Flask test CLI runner.
    """
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client: FlaskClient):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client: FlaskClient) -> AuthActions:
    """
    Return an instance of AuthActions that provides `login` and `logout` functions.
    """
    return AuthActions(client)
