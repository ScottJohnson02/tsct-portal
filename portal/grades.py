from flask import (
    Blueprint, g, render_template, redirect, url_for, session, request, flash
)
from portal.auth import teacher_required, login_required
from portal.db import get_db
from portal.sessions import course

bp = Blueprint('grades', __name__)


@bp.route('/grades', methods=("GET", "POST"))
@teacher_required
def grades():
    course_id = request.args.get('course_id')
    section = request.args.get('section')
    assign_id = request.args.get('assignment_id')

    assignments = assignments_info(assign_id)
    name = assignments[0][0]
    points = assignments[0][1]

    if request.method == "POST":
        student = request.form.getlist('student')
        points_earned = request.form.getlist('grade')
        graded = check_graded(assign_id, student)

        if not graded:
            grade_for(student[0], points_earned[0], assign_id)

    students = students_assigned(course_id, section)
    all_grades = get_grades(assign_id)
    course_name = course(course_id)


    grades_dict = {}
    for grade in all_grades:
        grades_dict[grade['student_sessions_id']] = grade['points_earned']

    return render_template("portal/entergrades.html",
                            name=name, points=points,
                            course_id=course_id,
                            students=students,
                            section=section,
                            course_name=course_name,
                            grades_dict=grades_dict)

@bp.route('/viewgrades/<int:course_id>/<section>', methods=("GET",))
@teacher_required
def view_session_grades(course_id, section):
    classname = request.args.get('classname')
    # gets all students in class
    students = students_assigned(course_id, section)
    # gets all assignments in the section
    student_assignments = get_student_assignments(course_id, section)
    # possible points for the course
    total_points = 0
    total_earned = 0
    grade_letter = '--'
    percent = 0
    for student in students:
        student_points = 0
        student_possible = 0
        for assignment in student_assignments:
            if student['id'] == assignment[8]:
                if assignment[9] != None:
                    student_possible = student_possible + assignment[5]
                    student_points = student_points + assignment[9]
        student.append(student_possible)
        student.append(student_points)

    for assignment in student_assignments:
        total_points = total_points + assignment[5]
        if assignment[9] != None:
            total_earned = total_earned + assignment[9]
    if total_points != 0:
        percent = total_earned / total_points * 100
        percent = round(percent, 2)
        grade_letter = grade_calc(percent)

    return render_template("portal/allgrades.html",
                           students=students,
                           course_id=course_id,
                           section=section,
                           total_points=total_points,
                           classname=classname,
                           total_earned=total_earned,
                           grade_letter=grade_letter,
                           percent=percent)

def assignments_info(assign_id):
    # Grabs Name and points for assignment id
    cur = get_db().cursor()
    cur.execute("""SELECT name, points FROM assignments
                   WHERE id = %s;""",
                (assign_id,))

    return cur.fetchall()

# Grabs all grade records for the assignment id
def get_grades(assign_id):
    cur = get_db().cursor()
    cur.execute("""SELECT * FROM grades
                   WHERE assignment_id = %s;""",
                   (assign_id,))

    return cur.fetchall()

# Inserts grade info for called student and assignment id
def grade_for(student_sessions_id, points_earned, assignment_id):
    cur = get_db().cursor()
    cur.execute("""INSERT INTO grades (student_sessions_id, points_earned, assignment_id)
                   VALUES (%s, %s, %s)""",
                (student_sessions_id, points_earned, assignment_id))
    get_db().commit()
    cur.close()


# All info for students in the sessions
def students_assigned(course_id, section):
    cur = get_db().cursor()
    cur.execute("""SELECT * FROM users
                   JOIN student_sessions AS ss
                   ON users.id = ss.student_id
                   WHERE ss.course_id = %s AND ss.section = %s;""",
                (course_id, section))

    return cur.fetchall()


# Checks if student id and assignment id are in a record together
def check_graded(assign_id, student_id):
    cur = get_db().cursor()
    cur.execute("""SELECT * FROM Grades
                   WHERE assignment_id = %s
                   AND student_sessions_id = %s;""",
                (assign_id, student_id[0]))
    graded = cur.fetchall()

    if graded:
        return graded[0]
    else:
        return None


def get_student_assignments(course_id, section):
    cur = get_db().cursor()

    # Pulls out all assignments for the course
    cur.execute("""SELECT * FROM assignments a JOIN grades g
                   ON (a.id = g.assignment_id)
                   WHERE a.course_id = %s
                   AND a.section = %s;""",
                (course_id, section))

    assignments = cur.fetchall()
    return assignments


def grade_calc(percent):
    if percent > 90:
        grade = 'A'
    elif percent > 80:
        grade = 'B'
    elif percent > 70:
        grade = 'C'
    elif percent > 60:
        grade = 'D'
    elif percent < 60:
        grade = 'F'
    return grade
