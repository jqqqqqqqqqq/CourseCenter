from flask import render_template, redirect, url_for
from . import main
from .forms import EditSemesterForm
from flask_login import login_required, current_user
from .. import db
from ..models.models import Semester
import datetime


@main.route('/', methods=['GET', 'POST'])
def index():
    # return redirect(url_for('auth.login'))
    return render_template('index.html')


@main.route('/manage-semester', methods=['GET', 'POST'])
def manage_semester():
    semester_list = Semester.query.all()
    res = []
    for semester in semester_list:
        res.append({'id': semester.id,
                    'base_info': semester.base_info,
                    'time': semester.begin_time + '-' + semester.end_time})
    return render_template('manage_semester.html', res=res)


@main.route('/manage-course')
def manage_course():
    return render_template('manage_course.html')


@main.route('/index-teacher', methods=['GET', 'POST'])
def index_teacher():
    return render_template('auth_teacher/index_teacher.html')


@main.route('/index-teacher/teacher-course', methods=['GET', 'POST'])
def teacher_course():
    return render_template('auth_teacher/teacher_course.html')


@main.route('/index-teacher/teacher-resource', methods=['GET', 'POST'])
def teacher_resource():
    return render_template('auth_teacher/teacher_resource.html')


@main.route('/index-teacher/teacher-homework', methods=['GET', 'POST'])
def teacher_homework():
    return render_template('auth_teacher/teacher_homework.html')


@main.route('/index-teacher/teacher-communicate', methods=['GET', 'POST'])
def teacher_communicate():
    return render_template('auth_teacher/teacher_communicate.html')


@main.route('/index-teacher/teacher-teammanagement', methods=['GET', 'POST'])
def teacher_teammanagement():
    return render_template('auth_teacher/teacher_teammanagement.html')

