from flask import (
    Blueprint, g, render_template, redirect, url_for, session, request
)

from portal.db import get_db
from portal.auth import teacher_required, login_required
from portal.sessions import course

bp = Blueprint('assignments', __name__)

#-- Assignments --#
@bp.route('/assignments/<int:course_id>/<section>')
@login_required
def assignments(course_id, section):
    """View for the assignments"""
    if g.user['role'] == 'teacher':
        course_name = course(course_id)
        course_section = course_name + ' - ' + section

        # Grabs all the assignments user and session specific
        student_assignments = user_assignments(course_id, section)


        return render_template("portal/assignments.html",
                                    student_assignments=student_assignments,
                                    course_id=course_id,
                                    section=section,
                                    course_section=course_section,
                                    course_name=course_name)
    if g.user['role'] == 'student':
        course_name = course(course_id)
        course_section = course_name + ' - ' + section

        cur = get_db().cursor()
        total_earned = 0
        total_possible = 0
        student_assignments = get_student_assignments(course_id, section)
        for assignment in student_assignments:
            total_possible = total_possible + assignment[5]

            if assignment[9] != None:
                total_earned = total_earned + assignment[9]

        return render_template("portal/student_assignments.html",
                                student_assignments=student_assignments,
                                course_id=course_id,
                                section=section,
                                course_section=course_section,
                                course_name=course_name,
                                total_earned=total_earned,
                                total_possible=total_possible)

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

        cur = get_db().cursor()
        # make a query that inserts into assignments table with this info
        cur.execute("""INSERT INTO assignments
                       (course_id, section, name, type, points, due_date)
                       VALUES (%s, %s, %s, %s, %s, %s);""",
                       (course_id, section, name, type, points, duedate))
        get_db().commit()
        cur.close()

        return redirect(url_for('assignments.assignments',
                                 course_id=course_id,
                                 section=section))

    return render_template('portal/createassignment.html')

@bp.route('/assignments/<int:course_id>/<section>/<int:assignment_id>/viewdetails')
@login_required
def assignments_view(course_id, section, assignment_id):
    cur = get_db().cursor()

    # Pulls out all assignments for the course
    cur.execute("""SELECT * FROM assignments a JOIN grades g
                   ON (a.id = g.assignment_id)
                   WHERE a.course_id = %s
                   AND a.section = %s AND g.assignment_id = %s;""",
                   (course_id, section, assignment_id))

    details = cur.fetchone()
    course_name = course(course_id)

    return render_template('portal/assignments_view.html', details=details, course_name=course_name, section=section)

#-- Assignments for student/s --------------------------------------------------
def user_assignments(course_id, section):
    cur = get_db().cursor()

    # Pulls out all assignments for the course
    cur.execute("""SELECT * FROM assignments
                   WHERE course_id = %s
                   AND section = %s;""",
                   (course_id, section))

    assignments = cur.fetchall()
    return assignments

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
