from portal import create_app
import pytest

from flask import session


def test_config(monkeypatch):
    # Default config
    assert not create_app().testing

    # Test config
    assert create_app({'TESTING': True}).testing

    # Prod config
    monkeypatch.setenv('DATABASE_URL', "pretend this is on heroku...")
    assert "heroku" in create_app().config['DB_URL']
    assert "require" in create_app().config['DB_SSLMODE']


def test_index(client, auth):
    response = client.get('/')
    assert b"TSCT Portal" in response.data
    assert b'<form method="post">' in response.data


def test_login(client, auth):
    assert client.get('/').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/home'
    response = client.get('/home')
    assert b'Welcome' in response.data


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect email or password.'),
    ('test', 'a', b'Incorrect email or password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


# check logout
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'email' not in session
