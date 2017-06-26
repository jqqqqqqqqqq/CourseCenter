from app import db, login_manager


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

    def __repr__(self):
        return '<Semester %r>' % self.id


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.VARCHAR(length=50, convert_unicode=True))
    status = db.Column(db.Integer)
    reject_reason = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('课程 ID.id'), primary_key=True)

    def __repr__(self):
        return '<Semester %r>' % self.id


class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    team_name = db.Column(db.VARCHAR(length=50, convert_unicode=True))

    def __repr__(self):
        return '<Semester %r>' % self.id


class Homework(db.Model):
    __tablename__ = 'homework'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('课程 ID.id'), primary_key=True)
    base_requirement = db.Column(db.text)
    begin_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    weight = db.Column(db.Integer)
    max_submit_attempts = db.Column(db.Integer)

    def __repr__(self):
        return '<Semester %r>' % self.id


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    text_content = db.Column(db.text)
    score = db.Column(db.Integer)
    comments = db.Column(db.text)
    submit_attempts = db.Column(db.Integer)

    def __repr__(self):
        return '<Semester %r>' % self.id


class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), primary_key=True)
    guid = db.Column(db.text)
    status = db.Column(db.Boolean)

    def __repr__(self):
        return '<Semester %r>' % self.id
