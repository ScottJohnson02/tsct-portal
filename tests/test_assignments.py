import pytest

from portal.db import get_db

# get assignments that are assigned to the student


def test_view_assignments(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        # login as student
        auth.login()

        # get it
        response = client.get('/assignments/1/A')
        assert b'homework' in response.data


# see all assignments of a session
def test_view_session_assignments(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        # login as teacher
        auth.teacher_login()

        # get the assignments in the session
        response = client.get('/assignments/1/A')
        assert b'application' in response.data


def test_create_assignment(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        # login as teacher
        auth.teacher_login()

        # create a new software project section A assignment
        client.post('/createassignment?course_id=1&section=A', data={
            'name': 'top ten review', 'type': 'essay', 'points': '100', 'duedate': '01/10/2020'})

        response = client.get('/assignments/1/A')
        assert b'top ten review' in response.data

def test_assignment_detail_view(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.login()

        response = client.get('/assignments/1/A/1/viewdetails')
        assert b'Viewing homework' in response.data
        assert b'Due: 2020-05-01' in response.data
        assert b'Grade: 10 / 10' in response.data

def test_teacher_check(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        # login as student
        auth.login()

        # create a new software project section A assignment
        client.post('/createassignment?course_id=1&section=A', data={
            'name': 'top ten review', 'type': 'essay', 'points': '100', 'duedate': '01/10/2020'})

        response = client.get('/assignments?course_id=1&section=A')
        assert b'top ten review' not in response.data


def test_get_assignments(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        # login as teacher
        auth.teacher_login()

        # create a new software project section A assignment
        response = client.get('/createassignment?course_id=1&section=A')
        assert b'<input type="number" id="points" min="0" max="999" name="points" required>\n' in response.data
