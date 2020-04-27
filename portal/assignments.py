from flask import (
    Blueprint, g, render_template, redirect, url_for, session, request
)

from portal.db import get_db
from portal.auth import teacher_required, login_required

bp = Blueprint('assignments', __name__)

#-- Assignments --#
@bp.route('/assignments')
@login_required
def assignments():
    """View for the assignments"""
    course_id = request.args.get('course_id')
    section = request.args.get('section')
    coursename = course(course_id, section)

    # Grabs all the assignments user and session specific
    student_assignments = user_assignments(course_id, section)

    return render_template("portal/assignments.html",
                            student_assignments=student_assignments,
                            course_id=course_id,
                            section=section,
                            coursename=coursename)


#-- Create Assignments --#
@bp.route('/createassignment', methods=("GET", "POST"))
@teacher_required
def assignments_create():
    """View for creating an Assignment"""
    if request.method == "POST":
        course_id = request.args.get('course_id')
        section = request.args.get('section')
        name = request.form['name']
        type = request.form['type']
        points = request.form['points']
        duedate = request.form['duedate']

        # Gets all student ids in the given course_id and section
        sessions = student_sess_id(course_id, section)
        for students in sessions:

            cur = get_db().cursor()
            # make a query that inserts into assignments table with this info
            cur.execute("""INSERT INTO assignments
                           (course_id, section, name, type, points, due_date, student_sessions_id)
                           VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                           (course_id, section, name, type, points, duedate, students[0]))
            get_db().commit()
            cur.close()

        return redirect(url_for('assignments.assignments',
                                 course_id=course_id,
                                 section=section))

    return render_template('portal/createassignment.html')

#-- Gets all student id's that match course_id and section ---------------------
def student_sess_id(course_id, section):

    cur = get_db().cursor()
    cur.execute("""SELECT id
                   FROM student_sessions
                   WHERE course_id = %s AND section = %s;""",
                   (course_id, section))
    sessions = cur.fetchall()

    return sessions


#-- Assignments for student/s --------------------------------------------------
def user_assignments(course_id, section):
    # get the id of the student
    user = g.user['id']
    cur = get_db().cursor()

    #Shows students assingments
    if g.user['role'] == 'student':
        # pulls out all assignments for student id
        cur.execute("""SELECT * FROM assignments AS a
                       JOIN student_sessions AS ss
                       ON student_sessions_id = ss.id
                       WHERE ss.course_id = %s
                       AND ss.section = %s
                       AND ss.student_id = %s;""", (course_id, section, user))

    #Show teachers assignments
    if g.user['role'] == 'teacher':
    # Pulls out all assignments for the course
        cur.execute("""SELECT * FROM assignments AS a
                       JOIN sessions AS s
                       ON a.course_id = s.course_id AND a.section = s.section
                       WHERE a.course_id = %s AND a.section = %s;""", (course_id, section))

    student_assignments = cur.fetchall()
    return student_assignments


#-- Function for grabbing course and section -----------------------------------
def course(course_id, section):
    cur = get_db().cursor()
    # Course name where it matches course id
    cur.execute("""SELECT name FROM courses WHERE id = %s;""",
                (course_id,))
    course = cur.fetchall()[0][0]

    name = course + ' - ' + section
    return name
