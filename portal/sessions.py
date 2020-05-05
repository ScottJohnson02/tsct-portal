import os
from portal.db import get_db
from portal.auth import teacher_required, login_required
from portal.errorfuncs import validate_session, remove_prev_info, keep_prev_info

from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('sessions', __name__)

@bp.route('/sessions')
@login_required
def sessions_for_students():
    if g.user['role'] == 'teacher': # if a teacher tries to get here, redirect them to courses
        return redirect(url_for('courses.courses'))

    cur = get_db().cursor()

    cur.execute("""SELECT c.major, c.name, c.num, ss.course_id, ss.section
                   FROM student_sessions AS ss JOIN courses AS c
                   ON (ss.course_id = c.id) WHERE student_id = %s;""",
                   (g.user['id'],)) # getting course name, course id and section with a join
    all_student_sessions = cur.fetchall() # all the values are displayed with jinja2 in student_schedule.html
    cur.close()

    return render_template('portal/sessions/student_schedule.html', all_student_sessions=all_student_sessions)

@bp.route('/sessions/<int:course_id>')
@teacher_required
def sessions_for_teachers(course_id=None): # If no course_id is given, it is None
    cur = get_db().cursor()

    if(course_id == None): # if it is None, return them to courses
        return redirect(url_for('courses.courses'))

    cur.execute("""SELECT c.id, c.name, s.section
                   FROM sessions AS s JOIN courses AS c
                   ON (s.course_id = c.id)
                   WHERE s.teacher_id = %s AND s.course_id = %s;""",
                   (g.user['id'], course_id)) # gets course name, id, and section in a join

    all_teacher_sessions = cur.fetchall() # all rendered with jinja2 in sessions.html

    cur.close()

    return render_template('portal/sessions/sessions.html',
                            all_teacher_sessions=all_teacher_sessions,
                            course_id=course_id,
                            course_name=course(course_id))

# -- Function for grabbing course and section -----------------------------------


def course(course_id):
    cur = get_db().cursor()
    # Course name where it matches course id
    cur.execute("""SELECT name FROM courses WHERE id = %s;""",
                (course_id,))
    course_name = cur.fetchall()[0][0]

    name = course_name
    return name


@bp.route('/createsession', methods=("GET", "POST"))
@teacher_required
def session_create():
    """View for creating a session"""
    cur = get_db().cursor()
    course_id = request.args.get('course_id')

    cur.execute('SELECT * FROM users WHERE role = %s;', ('student',))
    all_students = cur.fetchall()

    if request.method == "POST":
        section = request.form['section']
        meeting_time = request.form['meeting']
        location = request.form['location']
        teacher_id = g.user['id']
        students = request.form.getlist('students')

        cur = get_db().cursor()
        check = validate_session(
            course_id, section, meeting_time, location, all_students)
        if check == True:
            cur.execute("""INSERT INTO sessions (course_id,section, meeting_time, location, teacher_id)
                            VALUES (%s, %s, %s, %s, %s);""", (course_id, section, meeting_time, location, teacher_id))
            get_db().commit()
            remove_prev_info('section')

            for student in students:
                # find student in user db then grab it by name
                cur = get_db().cursor()
                cur.execute('SELECT * FROM users WHERE name = %s;', (student,))
                student_info = cur.fetchone()
                student_id = student_info[0]
                # create a new session for each student
                cur.execute("""INSERT INTO student_sessions (course_id, section, student_id)
                                        VALUES (%s, %s, %s);""", (course_id, section, student_id))
                get_db().commit()
                cur.close()

            return redirect(url_for('sessions.sessions_for_teachers', course_id=course_id))
        else:
            return check

    return render_template('portal/sessions/createsession.html', all_students=all_students, course_id=course_id)

# @bp.route('/<int:course_id>/<section>/editsession', methods=("GET", "POST"))
# def session_edit(course_id, section):
#     """Edits the session name/info"""
#     cur = get_db().cursor()
#     teacher = g.user['id']
#     cur.execute("SELECT * FROM sessions WHERE section= %s AND course_id = %s;",
#                 (section, course_id))
#     selected_session = cur.fetchone()
#
#     if g.user['role'] == 'teacher':
#         return render_template('portal/home.html')
#
#     if request.method == "POST":
#         section = request.form['section']
#         meeting_time = request.form['meeting']
#         location = request.form['location']
#         teacher_id = g.user['id']
#         students = request.form.getlist('students')
#
#         cur.execute("DELETE FROM student_sessions WHERE section = %s AND course_id = %s;",
#                     (section, course_id))
#         # Remove all students from previous sessions
#
#         cur.execute(
#             """UPDATE sessions SET (course_id,section, meeting_time, location, teacher_id) = (%s, %s, %s, %s, %s)
#                 WHERE section = %s AND course_id = %s ;""", (course_id, section, meeting_time, location, teacher_id, section, course_id)
#         )
#
#         get_db().commit()
#         cur.close()
#
#         return redirect(url_for('courses.courses'))
#
#     return render_template("portal/sessions/editsession.html", course=course)

@bp.route('/viewsession/<int:course_id>/<section>/<classname>', methods=('GET', 'POST'))
@login_required
def session_view(course_id, section, classname):
    """View for seeing more session details."""
    cur = get_db().cursor()

    cur.execute(
        "SELECT * FROM sessions WHERE course_id = %s AND section = %s;", (course_id, section))
    session_info = cur.fetchone()

    return render_template('portal/sessions/viewsession.html', course_id=course_id, section=section,  classname=classname, session_info=session_info)


@bp.route('/deletesession', methods=("POST",))
@teacher_required
def session_delete():
    """View for deleting session"""
    course_id = request.form['course_id']
    section = request.form['section']
    teacher = g.user['id']
    cur = get_db().cursor()
    cur.execute("SELECT * FROM sessions WHERE  course_id= %s and section = %s",
                (course_id, section))
    session_information = cur.fetchone()
    if session_information['teacher_id'] != teacher:
        return redirect(url_for('sessions_for_teachers', course_id=course_id))

    if request.method == 'POST':
        cur.execute("SELECT * FROM assignments WHERE course_id= %s AND section = %s;",
                    (course_id, section))
        selected = cur.fetchall()

        cur.execute("DELETE FROM assignments WHERE (course_id= %s AND section = %s);",
                    (course_id, section))
        get_db().commit()
        cur.execute("DELETE FROM student_sessions WHERE  course_id= %s AND section = %s;",
                    (course_id, section))
        get_db().commit()
        cur.execute("DELETE FROM sessions WHERE course_id = %s AND section = %s;",
                    (course_id, section))
        get_db().commit()

        return redirect(url_for('courses.courses'))
