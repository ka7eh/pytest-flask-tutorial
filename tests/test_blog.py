import pytest
from _pytest.monkeypatch import MonkeyPatch
from flask import Flask
from flask.testing import FlaskClient

from flaskr.db import get_db

from .conftest import AuthActions


@pytest.mark.parametrize(
    ("session_user", "is_posts_author"),
    ((None, False), ("test", True), ("other", False))
)
@pytest.mark.parametrize(
    ("post", "is_published"),
    (
        ((b"test draft post", b"by test on 2018-01-01", b"test\ndraft body"), False),
        ((b"test published post", b"by test on 2017-01-01", b"test\npublished body"), True),
    )
)
def test_index(client: FlaskClient, auth: AuthActions, session_user, is_posts_author, post, is_published):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    if session_user:
        auth.login(username=session_user, password=session_user)
        response = client.get("/")
        assert b"Log Out" in response.data

    for item in post:
        if is_published or is_posts_author:
            assert item in response.data
        else:
            assert item not in response.data


@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete",))
def test_login_required(client: FlaskClient, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_author_required(app: Flask, client: FlaskClient, auth: AuthActions):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize("path", ("/3/update", "/3/delete",))
def test_exists_required(client: FlaskClient, auth: AuthActions, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client: FlaskClient, auth: AuthActions, app: Flask):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 3


def test_update(client: FlaskClient, auth: AuthActions, app: Flask):
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"


@pytest.mark.parametrize("path", ("/create", "/1/update",))
def test_create_update_validate(client: FlaskClient, auth: AuthActions, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in response.data


def test_delete(client: FlaskClient, auth: AuthActions, app: Flask):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "http://localhost/"

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None


def test_quotes_success(client: FlaskClient, monkeypatch: MonkeyPatch):
    def fake_request_get(url: str):
        class Response:
            def json(self):
                return {
                    "contents": {
                        "quotes": [
                            {
                                "quote": "LIBERATE QUOTES",
                                "author": "Michal Ondrejcek"
                            }
                        ]
                    }
                }
        return Response()
    monkeypatch.setattr("requests.get", fake_request_get)
    response = client.get("/")
    assert b"Michal" in response.data


def test_quotes_error(client: FlaskClient, monkeypatch: MonkeyPatch):
    """
    The quote API can return 429 if we send too many requests. The code should raise a warning if that happens.
    """

    def fake_request_get(url: str):
        class Response:
            def json(self):
                return {
                    "error": "429"
                }

        return Response()

    monkeypatch.setattr("requests.get", fake_request_get)
    with pytest.warns(UserWarning):
        client.get("/")
