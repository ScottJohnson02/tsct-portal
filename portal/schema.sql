-- TSCT Portal Database Schema
--
-- This file will drop and recreate all tables necessary for
-- the application and can be run with the `flask init-db`
-- command in your terminal.

-- Drop existing tables
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS users;


-- Users
CREATE TABLE users (
    id bigserial PRIMARY KEY,
    email text UNIQUE NOT NULL,
    password text NOT NULL,
    role varchar(7) NOT NULL CHECK (role IN ('teacher', 'student'))
);

-- Teachers
CREATE TABLE teachers (
  id serial PRIMARY KEY,
  teacher text UNIQUE NOT NULL,
  department text NOT NULL,
  num text NOT NULL
);

-- Courses
CREATE TABLE courses (
  id bigserial PRIMARY KEY,
  department text NOT NULL,
  num text UNIQUE NOT NULL,
  times text NOT NULL,
  campus text NOT NULL,
  buildingRoom text NOT NULL,
  credits integer NOT NULL,
  teacher text UNIQUE NOT NULL users (id)
);

-- Roster
CREATE TABLE roster (
  id serial PRIMARY KEY,
  name text UNIQUE NOT NULL,
  addRemove text NOT NULL,
  status text NOT NULL
);

INSERT INTO teacher (teacher, department, num)
VALUES ('Teacher A', 'English', 'ENG 101'),
  ('Teacher B', 'Math', 'MATH 202'),
  ('Teacher C', 'Welding Freshmen', 'WELD 102'),
  ('Teacher D', 'Computer Software Engineering Technology Freshmen', 'CSET 102'),
  ('Teacher D', 'Computer Software Engineering Technology Sophomores', 'CSET 202'),
  ('Teacher D', 'Welding Sophomores', 'WELD 202');


INSERT INTO courses (department, num, times, campus, buildingRoom, credits)
VALUES ('English', 'ENG 101', '10:00am - 11:00am', 'Main', 'Mellor 204', '3'),
  ('English', 'ENG 101', '8:00am - 9:00am', 'Main', 'Mellor 204', '3'),
  ('Math', 'MATH 202', '10:30am - 11:45am','Main', 'Mellor 202', '3'),
  ('Math', 'MATH 202', '7:45am - 9:30am', 'Main', 'Mellor 305', '3'),
  ('Welding Freshmen', 'WELD 102', '12:00 - 4:30pm MTRF, 12:30am - 4:30pm W', 'Greenfield', 'Shop #2', '3'),
  ('Computer Software Engineering Technology Freshmen', '12:00 - 4:30pm MTRF, 12:30am - 4:30pm W', 'Greenfield', 'Shop #3', '3'),
  ('Computer Software Engineering Technology Sophomores', 'CSET 202', '7:00am - 11:30am MTRF, 7:30am - 12:00pm W', 'Greenfield', 'Shop #3', '3'),
  ('Welding Sophomores', 'WELD 202', '7:00am - 11:30am MTRF, 7:30am - 12:00pm W', 'Greenfield', 'Shop #2', '3');


INSERT INTO roster (name, addRemove, status)
VALUES ('Student A', '+', 'Not on roster'),
  ('Student B', '+', 'Not on roster'),
  ('Student C', '+', 'Not on roster'),
  ('Student D', '+', 'Not on roster'),
  ('Student E', '+', 'Not on roster'),
  ('Student F', '+', 'Not on roster'),
  ('Student G', '+', 'Not on roster'),
  ('Student H', '+', 'Not on roster');
