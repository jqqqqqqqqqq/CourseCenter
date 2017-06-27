import os

from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app.models.models import Student, Teacher, DeanInfo, Semester, Team, TeamMember, Homework ,Submission, Attachment, Course, CourseTime, TeacherTeam

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)



if __name__ == '__main__':
    manager.run()
