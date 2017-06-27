from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class DeanInfo(UserMixin, db.Model):
    __tablename__ = 'deanInfo'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_id(self):
        return self.id

    def __repr__(self):
        return '<DeanInfo %r>' % self.id


class Semester(db.Model):
    __tablename__ = 'semesters'
    id = db.Column(db.Integer, primary_key=True)
    base_info = db.Column(db.Text)
    begin_time = db.Column(db.Date)
    end_time = db.Column(db.Date)

    def __repr__(self):
        return '<Semester %r>' % self.id


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.VARCHAR(length=50, convert_unicode=True))
    role = db.Column(db.Integer)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Student %r>' % self.id


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.VARCHAR(length=50, convert_unicode=True))
    status = db.Column(db.Integer)
    reject_reason = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)

    def __repr__(self):
        return '<Team %r>' % self.id


class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    team_name = db.Column(db.VARCHAR(length=50, convert_unicode=True))

    def __repr__(self):
        return '<TeamMember %r>' % self.id


class Homework(db.Model):
    __tablename__ = 'homework'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    base_requirement = db.Column(db.Text)
    begin_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    weight = db.Column(db.Integer)
    max_submit_attempts = db.Column(db.Integer)

    def __repr__(self):
        return '<Homework %r>' % self.id


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    text_content = db.Column(db.Text)
    score = db.Column(db.Integer)
    comments = db.Column(db.Text)
    submit_attempts = db.Column(db.Integer)

    def __repr__(self):
        return '<Submission %r>' % self.id


class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), primary_key=True)
    guid = db.Column(db.Text)
    status = db.Column(db.Boolean)

    def __repr__(self):
        return '<Attachment %r>' % self.id


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    teacherTeam_id = db.Column(db.Integer, db.ForeignKey('teacher_teams.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'))
    course_info = db.Column(db.Text)
    place = db.Column(db.String(50))
    outline = db.Column(db.Text)
    credit = db.Column(db.Integer)
    teamsize = db.Column(db.Integer)

    def __repr__(self):
        return '<Course %r>' % self.id


class CourseTime(db.Model):
    __tablename__ = 'course_time'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    start_week = db.Column(db.Integer)
    start_section = db.Column(db.Integer)
    finish_section = db.Column(db.Integer)

    def __repr__(self):
        return '<CourseTime %r>' % self.id


class TeacherTeam(db.Model):
    __tablename__ = 'teacher_teams'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))

    def __repr__(self):
        return '<TeacherTeam %r>' % self.id


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    teacher_info = db.Column(db.Text)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Teacher %r>' % self.id


@login_manager.user_loader
def load_user(user_id):
    temp = DeanInfo.query.get(int(user_id))
    if temp:
        return temp
    temp = Teacher.query.get(int(user_id))
    if temp:
        return temp
    return Student.query.get(int(user_id))
