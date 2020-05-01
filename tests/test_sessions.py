import pytest

from portal.db import get_db


# get sessions page as student where they are enrolled in
def test_view_sessions(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        # login as student
        auth.login()

        # get it
        response = client.get('/sessions')
        assert response.data.count(b'Software Project II') == 2


# see all sessions of a class
def test_view_course_sessions(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        # login as teacher
        auth.teacher_login()

        # get the sessions in the class
        response = client.get('/sessions/1')
        assert response.data.count(b'Software Project II') == 2


# create sessions

def test_create_session(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        # login as teacher
        auth.teacher_login()

        # create a new software project session
        client.post('/createsession?course_id=2', data={
            'section': 'H', 'meeting': '09:18', 'location': '100', 'students': 'kyle'})

        response = client.get('/sessions/1')
        assert response.data.count(b'Software Project II') == 2

def test_view_sessions(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.teacher_login()

        response = client.get(
            '/viewsession/1/B/Software%20Project%20II')

        assert b"Software Project I" in response.data
        assert b"Session Time" in response.data


def test_delete_sessions(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.teacher_login()

        response = client.post(
            '/deletesession', data={'course_id': 1, 'section': 'A'})
        cur.execute(
            "SELECT * FROM sessions WHERE section = 'A' and course_id = '1';")
        check = cur.fetchone()
        assert check is None


@pytest.mark.parametrize(('url'), (
    ('/createsession'),
    ('/courses'),
    ('/deletesession')
))
def test_teacher_check(app, client, auth, url):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.login()
        if url == '/deletesession':
            response = client.post(url, data={'course_to_delete': 4})
        else:
            response = client.get(url)

        assert b'Redirect' in response.data


@pytest.mark.parametrize(('role'), (
    ('teacher'),
    ('student'),
))
def test_session_role(app, client, auth, role):
    with app.app_context():
        if role == 'teacher':
            auth.teacher_login()
            request = client.get('/sessions')
            course = client.get('/courses')
            assert b'tically to target URL: <a href="/courses">/courses</a>.' in request.data
        else:
            auth.login()
            request = client.get('/sessions')
            assert b'Software Project II' in request.data
