from flask import flash, redirect, render_template, url_for, request
from datetime import datetime
from flask_login import login_required
from . import teacher
from .. import db
from ..auths import UserAuth
from .forms import CourseForm, HomeworkForm, UploadResourceForm, upsr, AcceptTeam, RejectTeam
from ..models.models import Course, Homework, Team, TeamMember, Student
import uuid
from flask_uploads import UploadNotAllowed
import os
from config import basedir

@teacher.before_request
@login_required
def before_request():
    pass


@teacher.route('/<course_id>/course', methods=['GET', 'POST'])
@UserAuth.teacher_course_access
def set_course_info(course_id):
    form = CourseForm()
    course = Course.query.filter_by(id=course_id).first()
    if form.validate_on_submit():
        course.outline = form.outline.data
        course.teamsize_min = form.teamsize_min.data
        course.teamsize_max = form.teamsize_max.data
        db.session.add(course)
        db.session.commit()
        flash('修改成功！', 'success')
        return redirect(url_for('teacher.set_course_info', course_id=course_id))
    form.outline.data = course.outline
    form.teamsize_min.data = course.teamsize_min
    form.teamsize_max.data = course.teamsize_max
    return render_template('teacher/course.html', course_id=course_id, form=form, course=course)


@teacher.route('/<course_id>/resource', methods=['GET', 'POST'])
@UserAuth.teacher_course_access
def manage_resource(course_id):
    return render_template('teacher/resource.html', course_id=course_id)


@teacher.route('/<course_id>/homework', methods=['GET', 'POST'])
@UserAuth.teacher_course_access
def set_homework(course_id):

    form = HomeworkForm()
    if form.validate_on_submit():
        begin_time, end_time = form.time.data.split(' - ')
        begin_time = datetime.strptime(begin_time, '%m/%d/%Y %H:%M')
        end_time = datetime.strptime(end_time, '%m/%d/%Y %H:%M')

        # 可能是edit或者是add
        if request.args.get('action') == 'edit':
            homework = Homework.query.filter_by(id=request.args.get('homework_id')).first()
        else:
            homework = Homework()

        homework.name = form.name.data
        homework.base_requirement = form.base_requirement.data
        homework.begin_time = begin_time
        homework.end_time = end_time
        homework.weight = form.weight.data
        homework.max_submit_attempts = form.max_submit_attempts.data
        homework.course_id = course_id

        db.session.add(homework)
        db.session.commit()

        if request.args.get('homework_id'):
            flash('修改成功！', 'success')
            return redirect(url_for('teacher.set_homework',
                                    course_id=course_id,
                                    action='show',
                                    homework_id=request.args.get('homework_id')))
        flash('发布成功！', 'success')
        return redirect(url_for('teacher.set_homework', course_id=course_id))
    course = Course.query.filter_by(id=course_id).first()
    if request.args.get('action') == 'show':
        # 作业详情
        homework = Homework.query.filter_by(id=request.args.get('homework_id')).first()
        form.name.data = homework.name
        form.base_requirement.data = homework.base_requirement
        form.time.data = '{} - {}'.format(homework.begin_time.strftime('%m/%d/%Y %H:%M'),
                                          homework.end_time.strftime('%m/%d/%Y %H:%M'))
        form.weight.data = homework.weight
        form.max_submit_attempts.data = homework.max_submit_attempts

        return render_template('teacher/homework_detail.html',
                               course_id=course_id,
                               course=course,
                               form=form,
                               homework=homework)
    homework_list = Homework.query.filter_by(course_id=course_id).all()
    return render_template('teacher/homework.html', course_id=course_id, homeworks=homework_list, form=form, course=course)


@teacher.route('/uploadresource', methods=['GET', 'POST'])
def teacher_resource():
    form = UploadResourceForm()
    if form.validate_on_submit():
        try:
            (name, ext) = os.path.splitext(form.up.data.filename)
            filename = upsr.save(form.up.data, basedir + '/uploads/teacher_resources', name=str(uuid.uuid4())+ext)
            file_url = upsr.url(filename)
        except UploadNotAllowed:
            flash('附件上传不允许！', 'danger')
            return redirect(request.args.get('next') or url_for('uploadresource.html'))
    else:
        file_url = None
    return render_template('uploadresource.html', form=form, file_url=file_url)


@teacher.route('/index-teacher/teacher-teammanagement', methods=['GET', 'POST'])
def teacher_teammanagement():
    if "accept" in request.form.values():
        form = AcceptTeam()
        _team = Team.query.filter_by(id=int(form.id.data)).first()
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
        _team = Team.query.filter_by(id=int(form.id.data)).first()
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

    _team_list = Team.query.all()

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
        _team_members = TeamMember.query.filter_by(team_id=team.id).all()
        member_name = ""
        for member in _team_members:
            real_name = Student.query.filter_by(id=member.student_id).first().name
            member_name += member.team_name + "(" + real_name + "), "
        team.member_name = member_name  # 把所有人名字构造成一个字符串
        team.accept_form = AcceptTeam()
        team.accept_form.id.data = team.id
        team.reject_form = RejectTeam()
        team.reject_form.id.data = team.id
    return render_template('auth_teacher/teacher_teammanagement.html',
                           team_list=team_list)
