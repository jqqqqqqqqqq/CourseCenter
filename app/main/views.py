from flask import render_template, redirect, url_for, flash, request, session
from . import main
from .forms import AddSemesterForm
from .. import db
from ..models.models import Semester
import os, time
from datetime import date
from .forms import CourseForm, UploadForm
from app.models import models
from ..models.models import Student, Teacher

this_term = 1  # TODO: add semester selection
from werkzeug.utils import secure_filename
from flask import request
from .. import config, ups
import openpyxl
from config import basedir

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


def read_file(file_path):
    workbook = openpyxl.load_workbook(filename=file_path)  # 打开xls文件

    sheet_student = workbook.get_sheet_by_name('学生信息')
    sheet_teacher = workbook.get_sheet_by_name('老师信息')  # 通过sheet名字访问sheet
    student_info = []
    teacher_info = []
    for i in range(2, sheet_student.max_row + 1):
        student_list = {'id': sheet_student.cell(row=i, column=1).value,
                        'name': sheet_student.cell(row=i, column=2).value,
                        'password': 666}  # 学生初始密码 666
        student_info.append(student_list)
    for i in range(2, sheet_teacher.max_row + 1):
        teacher_list = {'id': sheet_teacher.cell(row=i, column=1).value,
                        'name': sheet_teacher.cell(row=i, column=2).value,
                        'teacher_info': sheet_teacher.cell(row=i, column=3).value,
                        'password': 666}  # 老师初始密码 666
        teacher_info.append(teacher_list)
    return student_info, teacher_info


@main.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = ups.save(form.up.data)
        file_url = ups.url(filename)
        file_path = os.path.join(basedir, 'uploads', filename)
        student_info, teacher_info = read_file(file_path=file_path)
        for i in student_info:
            student = Student.query.filter_by(id=i.get('id')).first()
            if student is None:
                student = Student()
            student.id = int(i.get('id'))
            student.name = i.get('name')
            student.password = str(i.get('password'))
            db.session.add(student)
        for i in teacher_info:
            teacher = Teacher.query.filter_by(id=i.get('id')).first()
            if teacher is None:
                teacher = Teacher()
            teacher.id = int(i.get('id'))
            teacher.name = i.get('name')
            teacher.teacher_info = i.get('teacher_info')
            teacher.password = str(i.get('password'))
            db.session.add(teacher)
        db.session.commit()
        os.remove(file_path)
    else:
        file_url = None
    return render_template('upload.html', form=form, file_url=file_url)


@main.route('/index-teacher', methods=['GET', 'POST'])
def index_teacher():
    return render_template('auth_teacher/index_teacher.html')


@main.route('/index-teacher/teacher-course', methods=['GET', 'POST'])
def teacher_course():
    return render_template('auth_teacher/teacher_course.html')


@main.route('/index-teacher/teacher-course_info', methods=['GET', 'POST'])
def teacher_course_info():
    semester_list = Semester.query.all()
    form = CourseForm()
    # form.semester.choices = [(a.id, str(a.id / 100) + '学年第' + str(a.id % 100) + '学期') for a in semester_list]
    # course = models.Course.query.filter_by(id=this_term).first()
    # session['course_id'] = course.id
    if 'action' in request.args:
        if request.args['action'] == 'edit':
            course = models.Course.query.filter_by(id=int(request.args['id'])).first()
            if not course:
                flash('找不到该课程', 'danger')
                return redirect(request.args.get('next') or url_for('main.teacher_course_info'))
            elif course.status is False:
                flash('课程已结束', 'too late')
                return redirect(request.args.get('next') or url_for('main.teacher_course_info'))
            course.course_info = form.course_info.data
            course.outline = form.outline.data
            db.session.commit()
            flash('修改成功！', 'success')
            return redirect(request.args.get('next') or url_for('main.teacher_course_info'))

    #     if request.args['action'] == 'delete':
    #         _course = models.Course.query.filter_by(id=int(request.args['id'])).first()
    #         if not _course:
    #             flash('找不到该课程', 'danger')
    #             return redirect(request.args.get('next') or url_for('main.manage_course'))
    #         db.session.delete(_course)
    #         db.session.commit()
    #         flash('删除成功', 'success')
    #         return redirect(request.args.get('next') or url_for('main.manage_course'))
    #     elif request.args['action'] == 'end':
    #         _course = models.Course.query.filter_by(id=int(request.args['id'])).first()
    #         if not _course:
    #             flash('找不到该课程', 'danger')
    #             return redirect(request.args.get('next') or url_for('main.manage_course'))
    #         _course.status = False
    #         db.session.commit()
    #         flash('结束成功', 'success')
    #         return redirect(request.args.get('next') or url_for('main.manage_course'))
    #
    # if form.validate_on_submit():
    #     if course.status is False
    #         flash('课程已结束', 'too late')
    #         return redirect(request.args.get('next') or url_for('main.teacher_course_info'))
    #     print(form.course_info.data)
    #     # _course = models.Course()
    #     # course = models.Course()
    #     # course.name = form.name.data
    #     course.course_info = form.course_info.data
    #     # course.place = form.place.data
    #     course.outline = form.outline.data
    #     # course.credit = int(form.credit.data)
    #     # course.teamsize = int(form.teamsize.data)
    #     # course.semester_id = form.semester.data
    #     # course.status = True
    #     # db.session.add(course)
    #     db.session.commit()
    #     flash('修改成功！', 'success')
    #     return redirect(request.args.get('next') or url_for('main.'))
    # # form.course_info.data = course.course_info
    # # form.place.data = course.place
    # # form.outline.data = course.outline
    # # form.credit.data = course.credit
    # # form.teamsize.data = course.teamsize
    course_list = models.Course.query.all()  # 显示课程
    return render_template('auth_teacher/teacher_course_info.html', form=form, courses=course_list, semesters=semester_list)    #负责人：李玮晨 状态：未测试


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


@main.route('/manage/course', methods=['GET', 'POST'])
def manage_course():
    semester_list = Semester.query.all()
    form = CourseForm()
    form.semester.choices = [(a.id, str(a.id / 100) + '学年第' + str(a.id % 100) + '学期') for a in semester_list]
    # course = models.Course.query.filter_by(id=this_term).first()
    # session['course_id'] = course.id
    if 'action' in request.args:
        if request.args['action'] == 'delete':
            _course = models.Course.query.filter_by(id=int(request.args['id'])).first()
            if not _course:
                flash('找不到该课程', 'danger')
                return redirect(request.args.get('next') or url_for('main.manage_course'))
            db.session.delete(_course)
            db.session.commit()
            flash('删除成功', 'success')
            return redirect(request.args.get('next') or url_for('main.manage_course'))
        elif request.args['action'] == 'end':
            _course = models.Course.query.filter_by(id=int(request.args['id'])).first()
            if not _course:
                flash('找不到该课程', 'danger')
                return redirect(request.args.get('next') or url_for('main.manage_course'))
            _course.status = False
            db.session.commit()
            flash('结束成功', 'success')
            return redirect(request.args.get('next') or url_for('main.manage_course'))

    if form.validate_on_submit():
        print(form.course_info.data)
        # _course = models.Course()
        course = models.Course()
        course.name = form.name.data
        course.course_info = form.course_info.data
        course.place = form.place.data
        course.outline = form.outline.data
        course.credit = int(form.credit.data)
        course.teamsize = int(form.teamsize.data)
        course.semester_id = form.semester.data
        course.status = True
        db.session.add(course)
        db.session.commit()
        flash('添加成功！', 'success')
        return redirect(request.args.get('next') or url_for('main.manage_course'))
    # form.course_info.data = course.course_info
    # form.place.data = course.place
    # form.outline.data = course.outline
    # form.credit.data = course.credit
    # form.teamsize.data = course.teamsize

    course_list = models.Course.query.all()  # 显示课程
    return render_template('manage/course.html', form=form, courses=course_list, semesters=semester_list)
