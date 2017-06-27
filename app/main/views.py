from flask import render_template, redirect, url_for, flash
from . import main
from .forms import AddSemesterForm
from .. import db
from ..models.models import Semester
import time
from datetime import date


@main.route('/', methods=['GET', 'POST'])
def index():
    # return redirect(url_for('auth.login'))
    return render_template('index.html')


@main.route('/manage-semester', methods=['GET', 'POST'])
def manage_semester():
    semester_list = Semester.query.all()
    semesters = []
    # for semester in semester_list:
    #     semesters.append({'id': semester.id,
    #                       'base_info': semester.base_info,
    #                       # 'time': semester.begin_time.strftime("%m/%d/%Y") + '-' + semester.end_time.strftime("%m/%d/%Y")})
    #                       'begin_time': semester.begin_time, 'end_time': semester.end_time})
    form = AddSemesterForm()
    if form.validate_on_submit():
        begin_time, end_time = form.time.data.split('-')
        month, day, year = begin_time.split('/')
        begin_time = date(int(year), int(month), int(day))
        month, day, year = end_time.split('/')
        end_time = date(int(year), int(month), int(day))
        db.session.add(Semester(id=form.id.data, base_info=form.base_info.data,
                                begin_time=begin_time, end_time=end_time))
        db.session.commit()
        flash('添加成功！')
    return render_template('manage_semester.html', form=form, semesters=semester_list)


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

