import pytest
from flask import g, session, Flask
from flask.testing import FlaskClient

from flaskr.db import get_db
from .conftest import AuthActions


def test_register(client: FlaskClient, app: Flask):
    assert client.get('/auth/register').status_code == 200
    response = client.post('/auth/register', data={'username': 'a', 'password': 'a'})
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute('SELECT * FROM user WHERE username = \'a\'').fetchone() is not None


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (
            ('', '', b'Username is required.'),
            ('a', '', b'Password is required'),
            ('test', 'test', b'already registered')
    )
)
def test_register_validate_input(client: FlaskClient, username, password, message):
    response = client.post('/auth/register', data={'username': username, 'password': password})
    assert message in response.data


def test_login(client: FlaskClient, auth: AuthActions):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (
            ('a', 'test', b'Incorrect username.'),
            ('test', 'a', b'Incorrect password.')
    )
)
def test_login_validate_input(auth: AuthActions, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client: FlaskClient, auth: AuthActions):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session


def test_password_strength():
    """
    TODO implement this
    Must check password strength criteria are being applied.
    """
    pass
