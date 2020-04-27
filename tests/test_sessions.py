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
        response = client.get('/sessions?course_id=1')
        assert response.data.count(b'Software Project II') == 3


# create sessions

def test_create_session(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        # login as teacher
        auth.teacher_login()

        # create a new software project session
        client.post('/createsession?course_id=1', data={
            'section': 'H', 'meeting': '09:18', 'location': '100', 'students': 'kyle'})

        response = client.get('/sessions?course_id=1')
        assert response.data.count(b'Software Project II') == 4


def test_view_sessions(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.teacher_login()

        response = client.get(
            '/viewsession?class=Software+Project+II&course_id=1&section=A')

        assert b"Software Project I" in response.data
        assert b"Session Time" in response.data


# def test_delete_sessions(app, client, auth):
#     with app.app_context():
#         db = get_db()
#
#         cur = db.cursor()
#
#         auth.teacher_login()
#
#         response = client.post('/deletesession', data={'course_to_delete': 4})
#         cur.execute("SELECT * FROM courses WHERE name = 'Security and Ethics';")
#         check = cur.fetchone()
#         assert check is None
