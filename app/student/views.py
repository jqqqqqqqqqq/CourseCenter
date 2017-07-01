import os, zipfile
from flask import render_template, flash, request, redirect, url_for, make_response, send_file, current_app, \
    send_from_directory
from flask_login import current_user
from . import student
from ..auths import UserAuth
from ..models.models import *
from .forms import *
from flask_uploads import UploadNotAllowed
from openpyxl.utils.exceptions import InvalidFileException
import uuid
from config import basedir
from sqlalchemy import or_

@student.route('/student')
@UserAuth.student_course_access
def index():
    return render_template('index.html')


# 提供打包的功能,需要根据实际情况修改
# 提供一个filelist，是一个list，包含的是目标多个文件的绝对路径
# output_filename是目标zip的名字
@student.route('/student/*****', methods=['GET'])
@UserAuth.student_course_access
def multi_download():
    filelist = request.args.get('filelist')
    output_filename = request.args.get('output_filename')
    zipf = zipfile.ZipFile(output_filename, 'w')
    [zipf.write(filename, filename.rsplit(os.path.sep, 1)[-1]) for filename in filelist]
    zipf.close()
    response = make_response(send_file(os.path.join(os.getcwd(), output_filename)))
    response.headers["Content-Disposition"] = "attachment; filename="+output_filename+";"
    return response


@student.route('/student/<course_id>/<file_name>', methods=['GET'])
@UserAuth.student_course_access
def download_resource(course_id, file_name):
    # 这里提供的是样例路径，具体根据实际路径修改

    # 文件是否存在
    if os.path.isfile(os.path.join(os.getcwd(), 'uploads', str(file_name))):
        response = make_response(send_file(os.path.join(os.getcwd(), 'uploads', str(file_name))))
    else:
        flash('选择的文件不存在')
        return redirect(url_for('index'))
    response.headers["Content-Disposition"] = "attachment; filename="+str(file_name)+";"
    return response


@student.route('/<course_id>/course', methods=['GET'])
@UserAuth.student_course_access
def show_course_info(course_id):
    # 学生查看课程信息
    course = Course.query.filter_by(id=course_id).first()
    return render_template('student/course.html', course_id=course_id, course=course)


@student.route('/<course_id>/resource', methods=['GET'])
@UserAuth.student_course_access
def show_resource(course_id):
    # 学生查看课程资源
    course = Course.query.filter_by(id=course_id).first()
    path = request.args.get('path')
    if not path:
        return redirect(url_for('student.show_resource', course_id=course_id, path='/'))
    expand_path = os.path.join(current_app.config['UPLOADED_FILES_DEST'], 'resource', course_id, path[1:])

    if not os.path.exists(expand_path):
        # 没有文件夹？赶紧新建一个，真鸡儿丢人
        os.mkdir(expand_path)

    if request.args.get('download'):
        # 下载
        filedir = os.path.join(
            current_app.config['UPLOADED_FILES_DEST'],
            'resource',
            course_id,
            path[1:])
        filename = request.args.get('filename')
        print(filename)
        if os.path.exists(os.path.join(filedir, filename)):
            return send_from_directory(filedir, filename, as_attachment=True)
        else:
            flash('文件不存在！', 'danger')
            redirect(url_for('teacher.manage_resource', course_id=course_id, path=path))

    files = list(os.scandir(expand_path))
    return render_template('student/resource.html', course_id=course_id, course=course, path=path, files=files)


@student.route('/student/<course_id>/submit/<homework_id>', methods=['GET', 'POST'])
def submit_homework(course_id, homework_id):
    form = HomeworkForm()
    team_member = TeamMember.query.filter_by(student_id=current_user.id).first()
    team = Team.query.filter_by(team_id=team_member.team_id).first()
    homework = Homework.query.filter_by(course_id=team.course_id).first()

    # 取这次提交前最新的submission记录 attachment记录
    submission_previous = Submission.query.filter_by(team_id=team_member.team_id).filter_by(homework_id=homework.id)[-1]
    attachment_previous = Attachment.query.filter_by(submission_id=submission_previous.id).first()

    if form.validate_on_submit():
        # 无法提交情况
        if current_user.id != team.owner_id:
            flash('权限不足，只有组长可以管理作业', 'danger')
            return redirect(request.args.get('next') or url_for('student.submit_homework'))
        elif submission_previous.submit_attempts >= homework.max_submit_attempts:
            flash('提交已达最大次数，无法提交', 'danger')
            return redirect(request.args.get('next') or url_for('student.submit_homework'))
        # 可以提交情况
        else:
            # 新建提交
            submission_1 = Submission()
            # 可能是edit或者add
            if request.args.get('action') == 'edit':
                submission_1 = submission_previous.submit_attempts + 1
            else:
                submission_1.submit_attempts = 1
            submission_previous.submit_status = 0
            submission_1.homework_id = homework.id
            submission_1.team_id = team.id
            submission_1.text_content = form.text_content.data
            submission_1.submitter_id = current_user.id
            submission_1.submit_status = 1  # 提交状态 1 已提交
            db.session.add(submission_1)
            db.session.add(submission_previous)
            db.session.commit()   # 提交更改 生成submission_1.id

            if form.homework_up.data:
                # 保存到uploads/<course-id>/<homework-id>/<team-id>
                guid = uuid.uuid4()
                try:
                    (name_temp, ext) = os.path.splitext(form.homework_up.data.filename)
                    homework_ups.save(form.homework_up.data,
                                      folder=os.path.join(basedir, 'uploads', str(course_id),
                                                          str(homework_id), str(team.id)),
                                      name=str(guid) + ext)
                except UploadNotAllowed:
                    flash('附件上传不允许！', 'danger')
                    return redirect(request.args.get('next') or url_for('main.submit_homework'))
                except InvalidFileException:
                    flash('附件类型不正确，请使用txt、doc、docx', 'danger')
                    return redirect(request.args.get('next') or url_for('main.submit_homework'))
                attachment = Attachment()
                attachment.submission_id = submission_1.id
                attachment.guid = guid
                attachment.status = False
                # 保存原文件名
                attachment.file_name = str(name_temp)
                db.ssession.add(attachment)
                db.session.commit()
                flash('提交成功!', 'success')
            return redirect(url_for('student.submit_homework', submission=submission_1, attachment=attachment, form=form))
    return render_template('/student/submit.html', submission=submission_previous, attachment=attachment_previous, form=form)


@student.route('/student/<course_id>/givegrade_stu', methods=['GET', 'POST'])
def givegrade_stu(course_id):
    team_member_1 = TeamMember.query.filter_by(student_id=current_user.id).first()
    team = Team.query.filter_by(id=team_member_1.team_id)
    team_member = TeamMember.query.filter_by(team_id=team.id).all()

    student_list = []

    # student_list用于在打分页面显示分数
    for i in team_member:
        student_temp = Student.query.filter_by(id=i.student_id).first()
        # student_list.append({student_temp.name: i.grade})
        student_list.append({'student_id': student_temp.id,
                             'student_name': student_temp.name,
                             'student_grade': i.grade})
    # 无法打分情况
    if request.method == 'POST':
        if current_user.id != team.owner_id:
            flash('权限不足，只有组长可以打分', 'danger')
            return redirect(request.args.get('next') or url_for('student.give_grade'))
        else:
            # key = student_id value = team_member.grade
            sum_total = 0
            for grade in request.form:
                sum_total += float(grade[-1])
            # 所有人的得分系数合应为1
            if sum_total > 1:
                flash('所有人的得分系数合应为1', 'danger')
                return redirect(url_for('student.givegrade_stu', student_list=student_list))
            else:
                for student_t in team_member:
                    student_t.grade = float(request.form.get[str(student_t.student_id)])
                    db.session.add(student_t)
                db.session.commit()
                flash('设置成功', 'success')
                return redirect(url_for('student.givegrade_stu', student_list=student_list))
    return render_template('/student/givegrade_stu.html', student_list=student_list)


@student.route('/<course_id>/teams', methods=['GET', 'POST'])
def team_view(course_id):
    form = CreateTeamForm()
    # 是不是团队队长
    team_owner = Team.query.filter_by(owner_id=current_user.id, course_id=course_id).first()
    # 是不是加入了团队
    team_joined = TeamMember.query.filter_by(student_id=current_user.id).filter_by(status=1).first()
    # 是不是在提交申请状态
    team_pending = TeamMember.query.filter_by(student_id=current_user.id).filter_by(status=0).first()
    if request.form.get('action') == 'join':
        # 加入团队
        member_list = TeamMember.query.filter_by(team_id=request.form.get('team_id')).filter_by(status=1).all()
        number_of_member = len(member_list)
        _course = Course.query.filter_by(id=course_id).first()
        if team_owner:
            flash('已创建团队，拒绝申请!', 'danger')
        elif team_joined:
            flash('已加入团队，拒绝申请!', 'danger')
        elif number_of_member == _course.teamsize_max - 1:
            flash('人数已满，拒绝申请！', 'danger')
        elif team_pending:
            flash('提交申请待审批，拒绝申请！', 'danger')
        else:
            teammember = TeamMember()
            teammember.team_id = request.form.get('team_id')
            teammember.student_id = current_user.id
            teammember.status = 0
            db.session.add(teammember)
            # delete_list = TeamMember.query.filter_by(status=2).filter_by(student_id=current_user.id).all()
            # for a in delete_list:
            #     db.session.delete(a)
            db.session.commit()
            flash('加入成功！', 'success')
        return redirect(url_for('student.team_view', course_id=course_id))
    elif request.form.get('action') == 'cancel':
        # 取消申请
        delete_teammember = TeamMember.query.filter_by(student_id=current_user.id).first()
        db.session.delete(delete_teammember)
        db.session.commit()
        flash('取消成功！', 'success')
        return redirect(url_for('student.team_view', course_id=course_id))

    if form.validate_on_submit():
        # 创建团队
        if team_owner:
            flash('已创建团队，无法再次创建!', 'danger')
        elif team_joined:
            flash('已加入团队，无法再次创建!', 'danger')
        elif team_pending:
            flash('提交申请待审批，拒绝申请！', 'danger')
        else:
            team = Team()
            team.status = 0
            team.course_id = course_id
            team.owner_id = current_user.id
            team.team_name = form.team_name.data
            db.session.add(team)
            db.session.commit()
            flash('创建团队成功!', 'success')
            return redirect(url_for('student.team_view', course_id=course_id))
    team_list_raw = Team.query.filter_by(course_id=course_id).filter(or_(Team.status == 0, Team.status == 3)).all()
    team_list = []
    for team in team_list_raw:
        # 计算团队人数
        member_list = TeamMember.query.filter_by(team_id=team.id).filter_by(status=1).all()
        number_of_member = len(member_list) + 1
        team_list.append({
            'id': team.id,
            'owner_id': team.owner_id,
            'team_name': team.team_name,
            'status': team.status,
            'number_of_member': number_of_member
        })
    return render_template('student/team.html',
                           teams=team_list,
                           form=form,
                           course_id=course_id,
                           unjoinable=team_owner or team_joined or team_pending,
                           pending=team_pending)


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
        if member_form.validate_on_submit():
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
        return render_template('student/team_manage.html', teammate_list=teammate_list, team=team)
    else:
        member = TeamMember.query.filter_by(student_id=student_id).first()
        if member:
            if member.status == 0:  # 等待申请
                team = Team.query.filter_by(owner_id=student_id).first()
                return render_template('student/pending.html')
            elif member.status == 1:  # 申请通过，展示团队
                team = Team.query.filter_by(id=member.team_id).first()
                if team.status == 4:  # 团队解散
                    return render_template('student/team_dismiss.html')
                teammate_list = TeamMember.query.filter_by(team_id=member.team_id)
                for member in teammate_list:
                    member.real_name = Student.query.filter_by(id=member.student_id).first().name
                    return render_template('student/team_info.html', teammate_list=teammate_list, team=team)
            elif member.status == 2:  # 被拒绝
                return render_template('student/reject.html')
        else:
            # 啥都不是，直接返回没有团队
            return render_template('student/no_team.html', course_id=course_id)
    return
