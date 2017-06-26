from app import db, login_manager


class Semester(db.Model):
    __tablename__ = 'semesters'
    id = db.Column(db.Integer, primary_key=True)
    base_info = db.Column(db.Text)
    start_time = db.Column(db.Date)
    finish_time = db.Column(db.Date)

    def __repr__(self):
        return '<Semester %r>' % self.id
