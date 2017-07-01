from flask import flash, redirect, render_template, url_for, request
from datetime import datetime
from flask_login import login_required
from . import teacher
from .. import db
from ..auths import UserAuth
from .forms import CourseForm, HomeworkForm
from ..models.models import Course, Homework


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
