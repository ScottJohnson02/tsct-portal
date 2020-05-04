-- Mock Data For Tests

INSERT INTO users (id, email, password, name, role, major)
VALUES (1, 'teacher@stevenscollege.edu', 'pbkdf2:sha256:150000$71PbcIFv$ffc17b1d44fa5ac0b5a9a1707b25e1c69b40a697676a6a30c374a57594b4df99', 'ms teacher', 'teacher', 'CSET'),
       (2, 'student@stevenscollege.edu', 'pbkdf2:sha256:150000$bhcUxUAk$b08d717a84c93c4d09afe712f0d781b216e5b77a27b9becbf4d535fde22d0e97', 'kyle', 'student', 'CSET'),
       (42267, 'duck@stevenscollege.edu', 'looney', 'Daffy Duck', 'teacher', 'WELD'),
       (50425, 'fflintstone425@stevenscollege.edu', 'bowling', 'Fred Flintstone', 'student', 'ARCH'),
       (13041, 'bsimpson041@stevenscollege.edu', 'iwillnot', 'Bart Simpson', 'student', 'ARCH');
-- courses
INSERT INTO courses (major, name, num, description, credits, teacher_id)
VALUES ('CSET', 'Software Project II', 180, 'blaaah', 3, 1),
       ('CSET', 'Web Development', 160, 'web dev lol', 3, 1),
       ('WELD', 'Metal', 105, 'weld', 3, 42267),
       ('CSET', 'Security and Ethics', 170, 'delete me', 3, 1);
-- sessions
INSERT INTO sessions (course_id, teacher_id, section, meeting_time, location)
VALUES (1, 1, 'A', 'now', 'here'), -- Software A
       (1, 1, 'B', 'now', 'place st'), -- Software B
       (2, 1, 'A', 'now', 'road st ave'); -- Web A

-- student sessions
INSERT INTO student_sessions (course_id, section, student_id)
VALUES (1,'A', 2), -- Software A
       (2,'A', 2), -- Web A
       (1,'B', 2); -- Software B

-- Assignments
INSERT INTO assignments (course_id,section, name, type, points, due_date)
VALUES (1, 'A', 'homework', 'paper', 10, 'now'),
       (1,'B', 'website', 'final', 50, 'now'),
       (1,'A', 'application', 'final', 100, 'now'),
       (2,'A', 'homework', 'paper', 10, 'now');

-- Grades
INSERT INTO grades (student_sessions_id, assignment_id, points_earned)
VALUES (1, 1, 10),
       (3, 2, 40);
