import os
from flask import render_template, flash, request, redirect, url_for, make_response, send_file
from flask_login import current_user
from . import student
from .. import db
from ..auths import UserAuth
from ..models.models import Course, TeamMember, Team, Homework, Submission, Attachment, Team, TeamMember
from .forms import HomeworkForm, homework_ups, CreateTeamForm
from flask_uploads import UploadNotAllowed
from openpyxl.utils.exceptions import InvalidFileException
import uuid
from config import basedir
from app.models import models


@student.route('/<course_id>/file/<file_name>', methods=['GET'])
@UserAuth.student_course_access
def download_resource(course_id, file_name):
    # 这里提供的是样例路径，具体根据实际路径修改
    response = make_response(send_file(os.getcwd() + '/uploads/' + str(file_name)))
    response.headers["Content-Disposition"] = "attachment; filename="+str(file_name)+";";
    return response


@student.route('/<course_id>/course', methods=['GET'])
@UserAuth.student_course_access
def show_course_info(course_id):
    course = Course.query.filter_by(id=course_id).first()
    return render_template('student/course.html', course_id=course_id, course=course)


@student.route('/<course_id>/homework/<homework_id>/submit', methods=['GET', 'POST'])
def submit_homework(course_id, homework_id):
    form = HomeworkForm()
    team_member = TeamMember.query.filter_by(student_id=current_user.id).first()
    team = Team.query.filter_by(team_id=team_member.team_id).first()
    homework = Homework.query.filter_by(course_id=team.course_id).first()

    # 取最新的submission记录 attachment记录
    submission = Submission.query.filter_by(team_id=team_member.team_id).filter_by(homework_id=homework.id).first()
    attachment_previous = Attachment.query.filter_by(submission_id=submission.id).first()

    if form.validate_on_submit():
        # 无法提交情况
        if current_user.id != team.owner_id:
            flash('权限不足，只有组长可以管理作业', 'danger')
        elif submission.submit_attempts >= homework.max_submit_attempts:
            flash('提交已达最大次数，无法提交', 'danger')
        # 可以提交情况
        else:
            if request.args.get('action') == 'edit':
                submission.submit_attempts += 1
                submission.text_content = form.text.data
                submission.submitter_id = current_user.id
                db.session.add(submission)

                if form.homework_up.data:
                    # 删除原来的作业附件
                    if attachment_previous:
                        os.remove(os.path.join(basedir, 'uploads', str(course_id),
                                               str(homework_id), attachment_previous.guid))
                    # 保存到uploads/<course-id>/<homework-id>
                    guid = uuid.uuid4()
                    try:
                        (name, ext) = os.path.splitext(form.up.data.filename)
                        filename = homework_ups.save(form.homework_up.data,
                                                     folder=os.path.join(basedir, 'uploads', str(course_id),
                                                                     str(homework_id)),
                                                     name=str(guid) + ext)
                    except UploadNotAllowed:
                        flash('附件上传不允许！', 'danger')
                        return redirect(request.args.get('next') or url_for('student.submit_homework'))
                    except InvalidFileException:
                        flash('附件类型不正确，请使用txt、doc、docx', 'danger')
                        return redirect(request.args.get('next') or url_for('student.submit_homework'))
                    attachment_previous.guid = guid
                    # 保存绝对路径
                    attachment_previous.file_name = str(filename)
                    db.ssession.add(attachment_previous)
                    db.session.commit()
                flash('更改成功!')
                return redirect(url_for('student.submit_homework', submission=submission, attachment=attachment_previous))
            else:
                # 新建提交
                submission = Submission()

                submission.submit_attempts = 1
                submission.homework_id = homework.id
                submission.team_id = team.id
                submission.text_content = form.text_content.data
                submission.submitter_id = current_user.id
                submission.submit_status = 1  # 提交状态 1 已提交
                db.session.add(submission)
                db.session.commit()   # 提交更改 生成submission_1.id

                if form.homework_up.data:
                    # 保存到uploads/<course-id>/<homework-id>
                    guid = uuid.uuid4()
                    try:
                        (name, ext) = os.path.splitext(form.up.data.filename)
                        filename = homework_ups.save(form.homework_up.data,
                                                     folder=os.path.join(basedir, 'uploads', str(course_id),
                                                                     str(homework_id)),
                                                     name=str(guid) + ext)
                    except UploadNotAllowed:
                        flash('附件上传不允许！', 'danger')
                        return redirect(request.args.get('next') or url_for('main.submit_homework'))
                    except InvalidFileException:
                        flash('附件类型不正确，请使用txt、doc、docx', 'danger')
                        return redirect(request.args.get('next') or url_for('main.submit_homework'))
                    attachment = Attachment()
                    attachment.submission_id = submission.id
                    attachment.guid = guid
                    attachment.status = False
                    # 保存绝对路径
                    attachment.file_name = str(filename)
                    db.ssession.add(attachment)
                db.session.commit()
                flash('提交成功!')
            return redirect(url_for('main.submit_homework', submission=submission, attachment=attachment))
    return render_template('/student/submit.html', submission=submission, attachment=attachment_previous)


@student.route('/<course_id>/teams', methods=['GET', 'POST'])
def team_view(course_id):
    form = CreateTeamForm()
    team_owner = Team.query.filter_by(owner_id=current_user.id).first()
    team_joined = TeamMember.query.filter_by(student_id=current_user.id).first()
    if request.args.get('action') == 'join':
        # 加入团队
        teammember = TeamMember()
        teammember.team_id = request.args['team_id'].data
        teammember.student_id = current_user.id.data
        teammember.team_name = request.args['team_name'].data
        db.session.add(teammember)
        db.session.commit()
        flash('加入成功！', 'success')
        return redirect(url_for('student.team_view'))
    if form.validate_on_submit():
        # 创建团队
        if team_owner:
            flash('已创建团队，无法再次创建!', 'danger')
        elif team_joined:
            flash('已加入团队，无法再次创建!', 'danger')
        else:
            team = Team()
            team.status = 0
            team.course_id = form.course_id.data
            team.owner_id = current_user.id.data
            team.team_name = form.team_name.data
            team.rejection_reason = ''
            db.session.add(team)
            db.session.commit()
            flash('创建团队成功!', 'success')
            current_team = Team.query.filter_by(owner_id=current_user.id).first()
            owner_member = TeamMember()
            owner_member.team_name = form.team_name.data
            owner_member.student_id = current_user.id.data
            owner_member.team_id = current_team.id.data
            db.session.add(owner_member)
            db.session.commit()
            return redirect(url_for('student.team_view'))
    team_list = Team.query.filter_by(course_id=course_id).filter_by(status=1).first()
    return render_template('/student/teams.html', teams=team_list)


@student.route('/<course_id>/my_team', methods=['GET', 'POST'])
def my_team(course_id):
    student_id = current_user.id
    owner = Team.query.filter_by(owner_id=student_id).first()  # 测试是不是队长
    if owner:
        # 如果是队长，则展示团队管理页面
        # TODO: 团队管理
        pass
    else:
        member = TeamMember.query.filter_by(student_id=student_id).first()
        if member:
            # 如果是队员，则展示团队信息
            # TODO：团队信息

            pass
        else:
            # 啥都不是，直接返回没有团队
            # TODO: 没有团队
            return render_template('/student/no_team.html')

    return
