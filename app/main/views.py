# -*- coding:utf-8 -*-
from flask import render_template, redirect, url_for, flash, request, session
from . import main
from .forms import AddSemesterForm
from .. import db
from ..models.models import Semester
import os, time
from datetime import date
from .forms import *
from app.models import models

this_term = 1  # TODO: add semester selection
from werkzeug.utils import secure_filename
from flask import request
from .. import config, ups
import openpyxl

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
        teacher_list = {'id': sheet_student.cell(row=i, column=1).value,
                        'name': sheet_student.cell(row=i, column=2).value,
                        'teacher_info': sheet_student.cell(row=i, column=3).value,
                        'password': 666}  # 老师初始密码 666
        teacher_info.append(teacher_list)
    return student_info, teacher_info


@main.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = ups.save(form.up.data)
        file_url = ups.url(filename)

    else:
        file_url = None
    return render_template('upload.html', form=form, file_url=file_url)


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
    if "accept" in request.form.values():
        form = AcceptTeam()
        _team = models.Team.query.filter_by(id=int(form.id.data)).first()
        if _team:
            _team.status = 1  # 1是通过
            db.session.add(_team)
            db.session.commit()
            flash("通过成功", "success")
            return redirect(request.args.get('next') or url_for('main.teacher_teammanagement'))
        else:
            flash("找不到此团队", "danger")
            return redirect(request.args.get('next') or url_for('main.teacher_teammanagement'))
    elif "reject" in request.form.values():
        form = RejectTeam()
        _team = models.Team.query.filter_by(id=int(form.id.data)).first()
        if _team:
            _team.status = 2  # 2是拒绝
            _team.reason = form.reason.data
            db.session.add(_team)
            db.session.commit()
            flash("拒绝成功", "success")
            return redirect(request.args.get('next') or url_for('main.teacher_teammanagement'))
        else:
            flash("找不到此团队", "danger")
            return redirect(request.args.get('next') or url_for('main.teacher_teammanagement'))

    _team_list = models.Team.query.all()

    class TeamList:
        id = 0
        status = 0
        team_name = ""

        def __init__(self, id, status, team_name):
            self.id = id
            self.status = status
            self.team_name = team_name

    team_list = [TeamList(a.id, a.status, a.team_name) for a in _team_list]
    for team in team_list:
        _team_members = models.TeamMember.query.filter_by(team_id=team.id).all()
        member_name = ""
        for member in _team_members:
            real_name = models.Student.query.filter_by(id=member.student_id).first().name
            member_name += member.team_name + "(" + real_name + "), "
        team.member_name = member_name  # 把所有人名字构造成一个字符串

        team.accept_form = AcceptTeam()
        team.accept_form.id.data = team.id

        team.reject_form = RejectTeam()
        team.reject_form.id.data = team.id
    return render_template('auth_teacher/teacher_teammanagement.html',
                           team_list=team_list)


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
