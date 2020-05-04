from flask import session, flash, render_template, redirect, url_for

from portal.db import get_db


# action is checked for what its being used for, *args is any number of other arguments
def keep_prev_info(action, *args):
    """Keeps the previously entered info in the create and edit queries. Used to keep info after page reload on error."""
    if action != "section":  # If used in courses module, save these keys to session object.
        session['cour_name'] = args[0]
        session['cour_num'] = args[1]
        session['cour_maj'] = args[2]
        session['cour_cred'] = args[3]
        session['cour_desc'] = args[4]

    if action == "section":  # If used in sessions module, save these keys to session object.
        session['section'] = args[0]
        session['meeting_time'] = args[1]
        session['location'] = args[2]


def remove_prev_info(action):  # action is checked for what its being used for.
    """Removes previous info from session once there are no errors found and the new object is created."""
    if action != "section":
        try:  # Delete the keys off of the session object.
            del session['cour_name']
            del session['cour_num']
            del session['cour_maj']
            del session['cour_cred']
            del session['cour_desc']
        # If the key doesn't exist, take to a different page. Should never get this error.
        except KeyError:
            redirect(url_for('courses.courses'))

    if action == "section":
        try:  # Deletes the keys off the session object.
            del session['section']
            del session['meeting_time']
            del session['location']
        except KeyError: # If the key doesn't exist, take to a different page. Should never get this error.
            redirect(url_for('courses.courses'))


def validate_query(action, course_id, *query_args):
    """Used to check query arguments when creating or editting a course."""
    cur = get_db().cursor()  # Allow use of DB
    errors = []  # Create empty list of errors

    cur.execute("SELECT * FROM courses WHERE name = %s AND id != %s;",
                (query_args[0], course_id))
    name_check = cur.fetchall()

    if name_check != []:  # If query was not empty, append an error to errors.
        name_error = "A course already exists with that name."
        errors.append(name_error)

    # If the course major input was given more than 4 letters, append an error to errors.
    if len(query_args[2]) > 4:
        maj_error = "Course Majors can only have a maximum of 4 letters."
        errors.append(maj_error)

    # If course credits input was given less than 1 or more than 4, append error to errors.
    if int(query_args[3]) > 4 or int(query_args[3]) < 0:
        cred_error = "A course can only have between 1 and 4 credits."
        errors.append(cred_error)

    # if course description input was given more than 200 characters, append an error to errors.
    if len(query_args[4]) > 200:
        desc_error = "Course descriptions should be a maximum of 200 characters."
        errors.append(desc_error)

    if errors != []:  # If there are errors in errors, flash them, keep previous input info in session, and reload the page.
        for error in errors:
            flash(error)
        if action == 'edit':  # If on edit view of courses module.
            keep_prev_info(
                action, query_args[0], query_args[1], query_args[2], query_args[3], query_args[4])
            # query_args[5] is the course's original info.
            return render_template('portal/editcourse.html', course=query_args[5])
        elif action == 'create':  # If on create view of courses module.
            keep_prev_info(
                action, query_args[0], query_args[1], query_args[2], query_args[3], query_args[4])
            return render_template('portal/createcourse.html')
    else:
        # If no errors in errors, return true to pass a check to go through with editing or creating a course.
        return True


def validate_session(course_id, section, *session_args):
    """Used for checking query arguments when creating a new course session."""
    cur = get_db().cursor()  # Allows for use of DB.
    errors = []  # Create an empty list of errors.

    cur.execute(
        """SELECT * FROM sessions WHERE course_id = %s and section = %s;""",
        (course_id, section))
    existingsection = cur.fetchall()

    if existingsection != []:  # If query was not empty, append error to errors.
        section_error = "That section already exists."
        errors.append(section_error)

    # If the date given was empty, append error to errors.
    if session_args[0] == "":
        time_error = "Please enter a valid time."
        errors.append(time_error)

    # If the location given was empty, append error to errors.
    if session_args[1] == "":
        location_error = "Please enter a location."
        errors.append(location_error)

    if errors != []:  # If errors is not empty, flash those errors and reload the page with all the info kept.
        for error in errors:
            flash(error)
            keep_prev_info('section', section,
                           session_args[0], session_args[1])
        # session_args[2] is required for createsession.
        return render_template('portal/createsession.html', all_students=session_args[2], course_id=course_id)
    else:
        # If no errors in errors, return true to pass a check to go through with creating the session.
        return True
