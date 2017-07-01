import os
from flask import render_template, flash, request, redirect, url_for, make_response, send_file
from flask_login import current_user
from . import student
from ..auths import UserAuth
from ..models.models import *
from .forms import *
from flask_uploads import UploadNotAllowed
from openpyxl.utils.exceptions import InvalidFileException
import uuid
from config import basedir


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
    team_owner = Team.query.filter_by(owner_id=current_user.id).filter_by(status=[0, 1, 2, 3]).first()
    team_joined = TeamMember.query.filter_by(student_id=current_user.id).filter_by(status=1).first()
    if request.args.get('action') == 'join':
        # 加入团队
        member_list = TeamMember.query.filter_by(team_id=request.args['course_id']).filter_by(status=1).all()
        number_of_member = len(member_list)
        _course = Course.query.filter_by(id=request.args['course_id']).first()
        if team_owner:
            flash('已创建团队，拒绝申请!', 'danger')
        elif team_joined:
            flash('已加入团队，拒绝申请!', 'danger')
        elif number_of_member == _course.teamsize-1:
            flash('人数已满，拒绝申请！', 'danger')
        elif TeamMember.query.filter_by(student_id=current_user.id).filter_by(status=0).first():
            flash('提交申请待审批，拒绝申请！', 'danger')
        else:
            teammember = TeamMember()
            teammember.team_id = request.args['team_id'].data
            teammember.student_id = current_user.id.data
            teammember.status = 0
            db.session.add(teammember)
            delete_list = TeamMember.query.filter_by(status=2).all()
            for a in delete_list:
                db.session.delete(a)
            db.session.commit()
            flash('加入成功！', 'success')
        return redirect(url_for('student.team_view'))
    elif request.args.get('action') == 'cancel':
        # 取消申请
        delete_teammember = TeamMember.query.filter_by(student_id=current_user.id).first()
        db.session.delete(delete_teammember)
        db.session.commit()
        return redirect(url_for('student.team_view'))
    if form.validate_on_submit():
        # 创建团队
        if team_owner:
            flash('已创建团队，无法再次创建!', 'danger')
        elif team_joined:
            flash('已加入团队，无法再次创建!', 'danger')
        elif TeamMember.query.filter_by(student_id=current_user.id).filter_by(status=0).first():
            flash('提交申请待审批，拒绝申请！', 'danger')
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
            return redirect(url_for('student.team_view'))
    team_list = Team.query.filter_by(course_id=course_id).filter_by(status=[0, 3]).all()
    return render_template('/student/teams.html', teams=team_list)


@student.route('/<course_id>/my_team', methods=['GET', 'POST'])
def my_team(course_id):
    student_id = current_user.id
    team = Team.query.filter_by(owner_id=student_id).first()  # 测试是不是队长
    if team:
        # 如果是队长，则展示团队管理页面
        teammate_list = TeamMember.query.filter_by(team_id=team.id)
        for member in teammate_list:
            member.real_name = Student.query.filter_by(id=member.student_id).first().name  # 通过member里的status在前端做通过/拒绝
        member_form = MemberForm()
        edit_team = EditTeam()
        if member.validate_on_submit():
            if request.args.get('action') == 'accept':
                member = TeamMember.query.filter_by(student_id=member_form.member_id.data).first()
                member.status = 1  # 1: Accepted
                db.session.add(member)
                db.session.commit()
                flash('接受成功', 'success')
            elif request.args.get('action') == 'reject':
                member = TeamMember.query.filter_by(student_id=member_form.member_id.data).first()
                member.status = 2  # 2: Rejected
                db.session.add(member)
                db.session.commit()
                flash('拒绝成功', 'success')
        elif edit_team.validate_on_submit():
            team.team_name = edit_team.new_name.data
            db.session.add(team)
            db.session.commit()
            flash('修改成功', 'success')
        elif request.args.get('action') == 'submit':
            team.status = 1  # 1: pending
            for member in teammate_list:
                if member.status == 0:  # 0: Pending
                    member.status = 2  # 2: Rejected
                    db.session.add(member)
            db.session.add(team)
            db.session.commit()
            flash('已提交申请', 'success')
        elif request.args.get('action') == 'dismiss':
            team.status = 4  # 4: dismiss
            for member in teammate_list:
                member.status = 2  # 2: Rejected
                db.session.add(member)
            db.session.add(team)
            db.session.commit()
            flash('队伍已解散', 'success')
        return render_template('/student/team_manage.html', teammate_list=teammate_list)
    else:
        member = TeamMember.query.filter_by(student_id=student_id).first()
        if member:
            if member.status == 0:  # 等待申请
                team = Team.query.filter_by(owner_id=student_id).first()
                return render_template('/student/pending.html')
            elif member.status == 1:  # 申请通过，展示团队
                team = Team.query.filter_by(id=member.team_id).first()
                if team.status == 4:  # 团队解散
                    return render_template('/student/team_dismiss.html')
                teammate_list = TeamMember.query.filter_by(team_id=member.team_id)
                for member in teammate_list:
                    member.real_name = Student.query.filter_by(id=member.student_id).first().name
                    return render_template('/student/team_info.html', teammate_list=teammate_list, team=team)
            elif member.status == 2:  # 被拒绝
                return render_template('/student/reject.html')
        else:
            # 啥都不是，直接返回没有团队
            return render_template('/student/no_team.html')
    return
