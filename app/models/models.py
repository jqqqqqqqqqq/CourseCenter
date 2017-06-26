from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class DeanInfo(UserMixin,db.Model):
    __tablename__ = 'deanInfo'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<DeanInfo %r>' % self.id

# 缺回调函数


class Semester(db.Model):
    __tablename__ = 'semesters'
    id = db.Column(db.Integer, primary_key=True)
    base_info = db.Column(db.Text)
    start_time = db.Column(db.Date)
    finish_time = db.Column(db.Date)

    def __repr__(self):
        return '<Semester %r>' % self.id


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    teacherTeam_id = db.Column(db.Integer, db.ForeignKey('teacherTeams.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'))
    course_info = db.Column(db.Text)
    place = db.Column(db.String(50))
    outline = db.Column(db.Text)
    credit = db.Column(db.Integer)
    teamsize = db.Column(db.Integer)

    def __repr__(self):
        return '<Course %r>' % self.id


class CourseTime(db.Model):
    __tablename__ = 'courseTime'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    start_week = db.Column(db.Integer)
    start_section = db.Column(db.Integer)
    finish_section = db.Column(db.Integer)

    def __repr__(self):
        return '<CourseTime %r>' % self.id


class TeacherTeam(db.Model):
    __tablename__ = 'teacherTeams'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))

    def __repr__(self):
        return '<TeacherTeam %r>' % self.id


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    teacher_info = db.Column(db.Text)

    def __repr__(self):
        return '<Teacher %r>' % self.id



