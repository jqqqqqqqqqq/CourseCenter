import os
import zipfile
import shutil
from flask import render_template, flash, request, redirect, url_for, make_response, send_file, current_app, \
    send_from_directory
from flask_login import login_required, current_user
from . import student
from ..auths import UserAuth
from ..models.models import *
from .forms import *
from flask_uploads import UploadNotAllowed
from openpyxl.utils.exceptions import InvalidFileException
import uuid
from config import basedir
from sqlalchemy import or_, and_
from datetime import datetime


@student.before_request
@login_required
def before_request():
    pass

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
            return redirect(url_for('teacher.manage_resource', course_id=course_id, path=path))
    files = []

    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Y', suffix)

    class file_attributes:
        name = ""
        size = ""
        create_time = datetime.min
        is_dir = False
        is_file = False

        def __init__(self, name, size, create_time, is_dir, is_file):
            self.name = name
            self.size = size
            self.create_time = create_time
            self.is_dir = is_dir
            self.is_file = is_file

    for file in os.scandir(expand_path):
        time = datetime.fromtimestamp(file.stat().st_mtime)
        files.append(file_attributes(file.name, sizeof_fmt(file.stat().st_size), time, file.is_dir(), file.is_file()))
    return render_template('student/resource.html', course_id=course_id, course=course, path=path, files=files)


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
            return redirect(url_for('student.givegrade_stu', course_id=course_id))
        else:
            # request.form: {student_id, grade}
            sum_total = 0

            for student_t in team_member:
                student_t.grade = float(request.form.get(student_t.student_id))
                sum_total = sum_total + float(student_t.grade)
                db.session.add(student_t)
            if sum_total == len(student_list):
                db.session.commit()
                flash('设置成功', 'success')
                return redirect(url_for('student.givegrade_stu', course_id=course_id))
            else:
                flash('所有人的得分系数平均为1', 'danger')
                return redirect(url_for('student.givegrade_stu', course_id=course_id))
    return render_template('/student/givegrade_stu.html', student_list=student_list)


@student.route('/<course_id>/teams', methods=['GET', 'POST'])
def team_view(course_id):
    form = CreateTeamForm()
    # 是不是团队队长
    team_owner = Team.query.filter_by(owner_id=current_user.id, course_id=course_id).first()
    # 是不是加入了团队
    team_joined = TeamMember\
        .query\
        .filter_by(student_id=current_user.id, status=1)\
        .join(Team)\
        .filter(Team.course_id == course_id)\
        .first()
    # 是不是在提交申请状态
    team_pending = TeamMember\
        .query\
        .filter_by(student_id=current_user.id, status=0) \
        .join(Team) \
        .filter(Team.course_id == course_id) \
        .first()

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

            # 学生团队管理要求删除被驳回记录
            delete_list = TeamMember.query.filter_by(status=2).filter_by(student_id=current_user.id).all()
            for record in delete_list:
                db.session.delete(record)
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

            delete_list = TeamMember.query.filter_by(status=2).filter_by(student_id=current_user.id).all()
            for record in delete_list:
                db.session.delete(record)
            db.session.commit()

            flash('创建团队成功!', 'success')
            return redirect(url_for('student.team_view', course_id=course_id))
    team_list = Team.query.filter_by(course_id=course_id).filter(or_(Team.status == 0, Team.status == 3)).all()
    return render_template('student/team.html',
                           teams=team_list,
                           form=form,
                           course_id=course_id,
                           unjoinable=team_owner or team_joined or team_pending,
                           pending=team_pending)


@student.route('/<course_id>/my_team', methods=['GET', 'POST'])
def my_team(course_id):
    # 团队管理
    student_id = current_user.id
    team = Team.query.filter_by(owner_id=student_id, course_id=course_id).first()  # 测试是不是队长
    teammate_list = []
    member_status = None
    if not team:
        # 如果不是队长的话
        member = TeamMember \
            .query \
            .filter_by(student_id=student_id) \
            .join(Team, TeamMember.team_id == Team.id)\
            .filter(Team.course_id == course_id) \
            .first()
        if member:
            team = Team.query.filter_by(id=member.team_id).first()
            member_status = member.status
    if team:
        teammate_list = team.members
        for member in teammate_list:
            member.real_name = Student.query.filter_by(id=member.student_id).first().name  # 通过member里的status在前端做通过/拒绝

    if team and request.form.get('action'):
        if request.form.get('action') == 'accept':
            # 接受成员
            member = TeamMember.query.filter_by(student_id=request.form.get('member_id')).first()
            member.status = 1  # 1: Accepted
            db.session.add(member)
            db.session.commit()
            flash('接受成功', 'success')
        elif request.form.get('action') == 'reject':
            # 拒绝成员
            member = TeamMember.query.filter_by(student_id=request.form.get('member_id')).first()
            member.status = 2  # 2: Rejected
            db.session.add(member)
            db.session.commit()
            flash('拒绝成功', 'success')
        elif request.form.get('action') == 'submit':
            # 提交团队组建申请
            _course = Course.query.filter_by(id=course_id).first()
            if team.number_of_members <= _course.teamsize_min:
                flash('人数不足', 'danger')
            else:
                team.status = 1  # 1: pending
                for member in teammate_list:
                    if member.status == 0:  # 0: Pending
                        member.status = 2  # 2: Rejected
                        db.session.add(member)
                db.session.add(team)
                db.session.commit()
                flash('已提交申请', 'success')
        elif request.form.get('action') == 'dismiss':
            # 解散团队
            for member in teammate_list:
                db.session.delete(member)
            db.session.delete(team)
            db.session.commit()
            flash('队伍已解散', 'success')
        elif request.form.get('action') == 'reset':
            team.status = 0
            db.session.add(team)
            db.session.commit()
        return redirect(url_for('student.my_team', course_id=course_id))

    return render_template('student/team_manage.html',
                           team=team,
                           course_id=course_id,
                           member_status=member_status)


@student.route('/<int:course_id>/homework')
@UserAuth.student_course_access
def homework(course_id):
    # 学生查看作业列表
    course = Course.query.filter_by(id=course_id).first()

    homework_list = Homework.query.filter_by(course_id=course_id).all()
    return render_template('student/homework.html', course_id=course_id, homeworks=homework_list, course=course)


@student.route('/<int:course_id>/homework/<int:homework_id>', methods=['GET', 'POST'])
@UserAuth.student_course_access
def homework_detail(course_id, homework_id):
    # 详细作业信息
    form = HomeworkForm()
    course = Course.query.filter_by(id=course_id).first()
    homework = Homework.query.filter_by(id=homework_id).first()
    team = Team.query.filter_by(owner_id=current_user.id, course_id=course_id).first()
    if not team:
        teammember = TeamMember\
                        .query\
                        .join(Team, Team.id == TeamMember.team_id)\
                        .filter(and_(TeamMember.student_id == current_user.id, Team.course_id == course_id))\
                        .first()
        team = Team.query.filter_by(id=teammember.team_id, course_id=course_id).first()
    attempts = len(Submission.query.filter_by(team_id=team.id, homework_id=homework_id).all())

    if form.validate_on_submit():
        # 无法提交情况
        if current_user.id != team.owner_id:
            flash('权限不足，只有组长可以管理作业', 'danger')
            return redirect(url_for('student.homework_detail', course_id=course_id, homework_id=homework_id))

        if attempts >= homework.max_submit_attempts:
            flash('提交已达最大次数，无法提交', 'danger')
            return redirect(url_for('student.homework_detail', course_id=course_id, homework_id=homework_id))
        submission = Submission()
        submission.homework_id = homework.id
        submission.homework_id = homework.id
        submission.team_id = team.id
        submission.text_content = form.text.data
        submission.submitter_id = current_user.id
        submission.score = 0
        db.session.add(submission)
        db.session.commit()   # 提交更改 生成submission_1.id

        # 每次提交新的作业 都会删除原来的作业附件
        path = os.path.join(basedir, 'uploads', str(course_id),
                            str(homework_id), str(team.id))
        # for i in os.listdir(path=path):
        #     os.remove(os.path.join(path + '\\' + str(i)))
        if os.path.exists(path):
            shutil.rmtree(path)

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
                return redirect(url_for('student.homework_detail', course_id=course_id, homework_id=homework_id))
            except InvalidFileException:
                flash('附件类型不正确!', 'danger')
                return redirect(url_for('main.submit_homework', course_id=course_id, homework_id=homework_id))
            attachment = Attachment()
            attachment.submission_id = submission.id
            attachment.guid = str(guid)
            attachment.upload_time = datetime.now()
            # 保存原文件名和扩展名
            attachment.file_name = str(name_temp) + ext
            db.session.add(attachment)
            db.session.commit()
            flash('提交成功!', 'success')
        return redirect(url_for('student.homework_detail', course_id=course_id, homework_id=homework_id))

    # 查找上一次提交
    submission_previous = Submission\
        .query\
        .filter_by(team_id=team.id,
                   homework_id=homework_id)\
        .order_by(Submission.id.desc())\
        .first()

    attachment_previous = None
    if submission_previous:
        attachment_previous = Attachment.query.filter_by(submission_id=submission_previous.id).first()

    return render_template('student/homework_detail.html',
                           course_id=course_id,
                           course=course,
                           homework=homework,
                           submission_previous=submission_previous,
                           attachment_previous=attachment_previous,
                           form=form,
                           team=team,
                           attempts=attempts)
