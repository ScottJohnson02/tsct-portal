import pytest

from portal.db import get_db


def test_course_page(client, auth):
    auth.teacher_login()

    response = client.get('/courses')

    assert b'Software Project II' in response.data


def test_create_course(app, client, auth):
    with app.app_context():  # allows DB queries to happen
        db = get_db()

        cur = db.cursor()

        auth.teacher_login()

        # post it
        response = client.post('/createcourse', data={'cour_maj': 'CSET', 'cour_name': 'test course',
                                                      'cour_num': 100, 'cour_desc': 'test description', 'cour_cred': 3})
        # check the db and see if that course exists now
        cur.execute("SELECT * FROM courses WHERE name = 'test course';")

        check = cur.fetchone()

        assert check['description'] == 'test description'
        assert check['name'] == 'test course'
        assert check['num'] == 100

        # check if it exists in that teacher's courses page
        courses_resp = client.get('/courses')

        assert b'test course' in courses_resp.data


def test_create_save_data(app, auth, client):
    auth.teacher_login()

    # post it
    response = client.post('/createcourse', data={'cour_maj': 'CSET', 'cour_name': 'Metal',
                                                  'cour_num': 100, 'cour_desc': 'test description', 'cour_cred': 3})
    # create a class that already exists
    assert b'A course already exists with that name.' in response.data


def test_edit_course(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.teacher_login()
        # post it again
        response = client.post('/1/editcourse', data={'cour_name': 'This is a test', 'cour_num': 111,
                                                      'cour_maj': 'CSET', 'cour_cred': 1, 'cour_desc': 'test description'})
        # check if it's been updated
        cur.execute("SELECT * FROM courses WHERE credits = 1")
        check = cur.fetchone()

        assert check['name'] == 'This is a test'
        assert check['credits'] == 1
        assert check['description'] == 'test description'

        # check if the change happened in that teacher's courses page
        courses_resp = client.get('/courses')

        assert b'This is a test' in courses_resp.data


def test_edit_save_data(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.teacher_login()
        # post it again
        response = client.post('/1/editcourse', data={'cour_name': 'Metal', 'cour_num': 111,
                                                      'cour_maj': 'CSET', 'cour_cred': 1, 'cour_desc': 'test description'})
        # check if it's been updated
        assert b'value="1"' in response.data


def test_course_id_length(app, client, auth):
    with app.app_context():
        auth.teacher_login()
        response = client.post('/createcourse', data={'cour_name': 'djhcd', 'cour_num': 111,
                                                      'cour_maj': 'CSETt', 'cour_cred': 1, 'cour_desc': 'test description'})
        assert b'Course Majors can only have a maximum of 4 letters.' in response.data
        # b'Course Majors can only have a maximum of 4 letters.'


def test_edit_course_id_length(app, client, auth):
    with app.app_context():
        auth.teacher_login()
        client.get('')
        response = client.post('/1/editcourse', data={'cour_name': 'something', 'cour_num': 111,
                                                      'cour_maj': 'CSETtt', 'cour_cred': 1, 'cour_desc': 'test description'})
        assert b'Course Majors can only have a maximum of 4 letters.' in response.data
        # b'Course Majors can only have a maximum of 4 letters.'


def test_delete_course(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.teacher_login()

        response = client.post('/deletecourse', data={'course_to_delete': 4})
        cur.execute("SELECT * FROM courses WHERE name = 'Security and Ethics';")
        check = cur.fetchone()

        assert check is None


@pytest.mark.parametrize(('url'), (
    ('/createcourse'),
    ('/1/editcourse'),
    ('/courses'),
    ('1/viewcourse'),
    ('/deletecourse')
))
def test_teacher_check(app, client, auth, url):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.login()
        if url == '/deletecourse':
            response = client.post(url, data={'course_to_delete': 4})
        else:
            response = client.get(url)

        assert b'Redirect' in response.data


def test_course_view(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.teacher_login()

        response = client.get('/1/viewcourse')

        assert b'Software Project II' in response.data
        assert b'blaaah' in response.data


def test_get_edit(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()

        auth.teacher_login()

        response = client.get('/1/editcourse')

        assert b'Software Project II' in response.data
        assert b'blaaah' in response.data
