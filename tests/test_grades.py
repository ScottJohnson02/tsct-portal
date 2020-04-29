import psycopg2
import pytest

from portal.db import get_db

# Join Table - To View
# SELECT a.name, g.points_earned a.points
# FROM assignments a, grades g
# WHERE g.assignment_id = a.id;

# Join Table - If Course ID is needed
# SELECT a.course_id, a.section, a.name, g.points_earned, a.points
# FROM assignments a, grades g
# WHERE g.assignment_id = a.id;

# get the grades page as a student here


# get the grades page as a teacher here
def test_view_grades_as_teacher(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        # login as teacher
        auth.teacher_login()

        # get the sessions in the class
        response = client.get('/grades?course_id=2&section=A&assignment_id=4')
        assert b'<input type="hidden" name="student" value="2">' in response.data


# update/add a grade as a teacher


def test_add_grade(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        cur.execute("SELECT * FROM Grades ")
        check = cur.fetchall()
        assert len(check) == 2

        # login as teacher
        auth.teacher_login()

        # get the sessions in the class
        response = client.post('/grades?course_id=2&section=A&assignment_id=4', data={
            'grade': 11, 'student': 2})

        cur.execute("SELECT * FROM Grades ")
        check = cur.fetchall()
        assert len(check) == 3

# check if it's changed
