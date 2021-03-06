import psycopg2
import pytest

from portal.db import get_db
from portal.grades import get_grades, grade_calc

# Join Table - To View
# SELECT a.name, g.points_earned a.points
# FROM assignments a, grades g
# WHERE g.assignment_id = a.id;

# Join Table - If Course ID is needed
# SELECT a.course_id, a.section, a.name, g.points_earned, a.points
# FROM assignments a, grades g
# WHERE g.assignment_id = a.id;

# get the grades page as a student here


def test_view_grades_as_student(app, client, auth):
    # login as student
    auth.login()

    # get the sessions in the class
    response = client.get('/assignments/1/A')
    assert b'Total Grade' in response.data
    # response = client.get( # url for grade page)
    #assert 'the grade field' in response.data


# get the grades page as a teacher here
def test_view_grades_as_teacher(app, client, auth):
    # login as teacher
    auth.teacher_login()

    # get the sessions in the class
    response = client.get('/grades?course_id=2&section=A&assignment_id=4')
    assert b'<input type="hidden" name="student" value="2">' in response.data

def test_view_overall_grades_as_teacher(app, client, auth):
    auth.teacher_login()

    response = client.get('/viewgrades/1/A?classname=Web+Development')
    assert b'Average Grade' in response.data

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

        # add a grade
        response = client.post('/grades?course_id=2&section=A&assignment_id=4', data={
            'grade': 11, 'student': 2})
        # check if it's changed
        cur.execute("SELECT * FROM Grades ")
        check = cur.fetchall()
        assert len(check) == 3

def test_duplicate_grade(app, client, auth):
    with app.app_context():
        db = get_db()

        cur = db.cursor()
        cur.execute("SELECT * FROM Grades ")
        check = cur.fetchall()
        assert len(check) == 2

        # login as teacher
        auth.teacher_login()
        # If duplicate grade
        client.post('/grades?course_id=2&section=A&assignment_id=4', data={
            'grade': 13, 'student': 2})
        # add a grade
        response = client.post('/grades?course_id=2&section=A&assignment_id=4', data={
            'grade': 11, 'student': 2})
        # check if it's changed
        cur.execute("SELECT * FROM Grades ")
        check = cur.fetchall()
        assert len(check) == 3

def test_functions(app, client, auth):
    with app.app_context():
        grade_query_results = get_grades(1)

        assert grade_query_results is not None

        letter_grade_results = grade_calc(50)

        assert letter_grade_results is not None
