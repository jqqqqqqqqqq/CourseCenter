from flask import render_template, redirect, url_for, flash, request, session
from . import main
from .forms import AddSemesterForm
from .. import db
from ..models.models import Semester
import os, time
from datetime import date
from .forms import CourseForm
from app.models import models

this_term = 1  # TODO: add semester selection
from werkzeug.utils import secure_filename
from flask import request
from .. import config

ALLOWED_EXTENSIONS = {"xls", "xlsx", "csv"}             # set(["xls", "xlsx"]) 允许上传的文件类型


@main.route('/', methods=['GET', 'POST'])
def index():
    # return redirect(url_for('auth.login'))
    return render_template('index.html')


@main.route('/manage/semester', methods=['GET', 'POST'])
def manage_semester():
    form = AddSemesterForm()
    if form.validate_on_submit():
        begin_time, end_time = form.time.data.split('-')
        month, day, year = begin_time.split('/')
        begin_time = date(int(year), int(month), int(day))
        month, day, year = end_time.split('/')
        end_time = date(int(year), int(month), int(day))
        if Semester.query.filter_by(id=form.id.data).first():
            flash('添加了重复的学期…', 'danger')
            return redirect(url_for('main.manage_semester'))
        db.session.add(Semester(id=form.id.data, base_info=form.base_info.data,
                                begin_time=begin_time, end_time=end_time))
        db.session.commit()
        flash('添加成功！', 'success')
        return redirect(url_for('main.manage_semester'))
    semester_list = Semester.query.all()
    return render_template('manage/semester.html', form=form, semesters=semester_list)

# 可能会使用的上传文件函数
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
#
#
# @main.route('/upload_file', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('uploaded_file',
#                                     filename=filename))



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


# @main.route('/set-course-info', methods=['GET', 'POST'])
# def set_course_info():
#     form = CourseForm()
#     course = models.Course.query.filter_by(id=this_term).first()
#     session['course_id'] = course.id
#     if form.validate_on_submit():
#         print(form.course_info.data)
#         # _course = models.Course()
#         course.course_info = form.course_info.data
#         course.place = form.place.data
#         course.outline = form.outline.data
#         course.credit = int(form.credit.data)
#         course.teamsize = int(form.teamsize.data)
#         db.session.commit()
#         return redirect(request.args.get('next') or url_for('main.set_course_info'))
#     form.course_info.data = course.course_info
#     form.place.data = course.place
#     form.outline.data = course.outline
#     form.credit.data = course.credit
#     form.teamsize.data = course.teamsize
#     return render_template('set_course_info.html', form=form)


@main.route('/manage/course', methods=['GET', 'POST'])
def manage_course():
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
        flash('编辑成功！', 'success')
        return redirect(request.args.get('next') or url_for('main.manage_course'))
    form.course_info.data = course.course_info
    form.place.data = course.place
    form.outline.data = course.outline
    form.credit.data = course.credit
    form.teamsize.data = course.teamsize
    return render_template('manage/course.html', form=form)


@main.route('/teacher', methods=['GET', 'POST'])
def teacher_index():
    # TODO: 这个是要被合并到主index里的 登陆做完之后应该通过获取用户组来判断进入那个index
    return render_template('teacher/index.html')


@main.route('/teacher/course', methods=['GET', 'POST'])
def set_course_info():
    return render_template('teacher/course.html')
