from flask import render_template, redirect, url_for, request, session
from . import main
from .forms import AddSemesterForm
from .. import db
from ..models.models import Semester
import time
from datetime import date
from .forms import CourseForm
from app.models import models

this_term = 1


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
                    'time': semester.begin_time.strftime("%m/%d/%Y") + '-' + semester.end_time.strftime("%m/%d/%Y")})
    form = AddSemesterForm()
    if form.validate_on_submit():
        begin_time, end_time = form.time.data.split('-')
        month, day, year = begin_time.split('/')
        begin_time = date(int(year), int(month), int(day))
        month, day, year = end_time.split('/')
        end_time = date(int(year), int(month), int(day))
        db.session.add(Semester(id=int(form.id.data), base_info=form.base_info.data,
                                begin_time=begin_time, end_time=end_time))
        db.session.commit()
        return redirect(url_for("main.manage_semester"))
    return render_template('manage_semester.html', form=form, res=res)


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


@main.route('/set-course-info', methods=['GET', 'POST'])
def set_course_info():
    form = CourseForm()
    course = models.Course.query.filter_by(id=this_term).first()
    session['course_id'] = course.id
    if form.validate_on_submit():
        print(form.course_info.data)
        # _course = models.Course()
        course.course_info = form.course_info.data
        course.place = form.place.data
        course.outline = form.outline.data
        course.credit = int(form.credit.data)
        course.teamsize = int(form.teamsize.data)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('main.set_course_info'))
    form.course_info.data = course.course_info
    form.place.data = course.place
    form.outline.data = course.outline
    form.credit.data = course.credit
    form.teamsize.data = course.teamsize
    return render_template('set_course_info.html', form=form)
