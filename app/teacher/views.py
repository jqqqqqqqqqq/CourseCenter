import shutil
from flask import flash, redirect, render_template, url_for, request,\
    current_app, send_from_directory, make_response, send_file
from datetime import datetime
from flask_login import login_required
from ..upload_utils import secure_filename
from . import teacher
from .. import db
from ..auths import UserAuth
from .forms import up_corrected, UploadCorrected,\
    CourseForm, HomeworkForm, UploadResourceForm, upsr, AcceptTeam, RejectTeam
from ..models.models import Course, Homework, Team, TeamMember, Student, Submission, Attachment
import uuid
from flask_uploads import UploadNotAllowed
import os, zipfile
from openpyxl.utils.exceptions import InvalidFileException
from config import basedir


@teacher.before_request
@login_required
def before_request():
    pass


@teacher.route('/<course_id>/course', methods=['GET', 'POST'])
@UserAuth.teacher_course_access
def set_course_info(course_id):
    # 教师课程信息
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
    # 教师课程资源
    path = request.args.get('path')
    if not path:
        return redirect(url_for('teacher.manage_resource', course_id=course_id, path='/'))

    expand_path = os.path.join(current_app.config['UPLOADED_FILES_DEST'], 'resource', course_id, path[1:])
    if not os.path.exists(expand_path):
        # 没有文件夹？赶紧新建一个，真鸡儿丢人
        os.mkdir(expand_path)

    if request.method == 'POST' and 'file' in request.files:
        # 上传文件
        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOADED_FILES_DEST'], 'resource', course_id, path[1:], filename)
        if os.path.exists(filepath):
            flash('已经存在了同名文件', 'danger')
            return redirect(url_for('teacher.manage_resource', course_id=course_id, path=path))
        file.save(filepath)
        flash('上传成功！', 'success')
        return redirect(url_for('teacher.manage_resource', course_id=course_id, path=path))

    if request.method == 'POST' and 'dirname' in request.form:
        # 新建文件夹
        dirname = request.form['dirname']
        dirpath = os.path.join(current_app.config['UPLOADED_FILES_DEST'], 'resource', course_id, path[1:], dirname)
        if os.path.exists(dirpath):
            flash('已经存在了同名文件夹', 'danger')
            return redirect(url_for('teacher.manage_resource', course_id=course_id, path=path))
        os.mkdir(dirpath)
        flash('新建文件夹成功！', 'success')
        return redirect(url_for('teacher.manage_resource', course_id=course_id, path=path))

    if 'action' in request.form:
        if request.form.get('action') == 'delete':
            # 删除
            filepath = os.path.join(
                current_app.config['UPLOADED_FILES_DEST'],
                'resource',
                course_id,
                path[1:],
                request.form.get('filename')
            )
            if not os.path.exists(filepath):
                flash('文件不存在！', 'danger')
                redirect(url_for('teacher.manage_resource', course_id=course_id, path=path))
            if os.path.isfile(filepath):
                os.remove(filepath)
            else:
                shutil.rmtree(filepath)
            flash('删除成功！', 'success')
            redirect(url_for('teacher.manage_resource', course_id=course_id, path=path))

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
    return render_template('teacher/resource.html', course_id=course_id, files=files, path=path)


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


#上传老师批改后的作业
def teacher_corrected(course_id, homework_id):
    form = UploadCorrected()
    if form.validate_on_submit():
        if form.up_corrected:
            try:
                name_temp, ext = os.path.splitext(form.up_corrected.data.filename)
                # 保存文件在basedir/uploads/<course_id>/<homework_id>/teacher_corrected.ext (通过特定名字找下载)
                up_corrected.save(form.up_corrected,
                                  folder=os.path.join(basedir, 'uploads', str(course_id), str(homework_id)),
                                  name=u'teacher_corrected' + ext)
            except InvalidFileException:
                flash(u'附件类型不正确，请使用zip或rar', 'danger')
                return redirect(request.args.get('next') or url_for('teacher.teacher_corrected'))
            except UploadNotAllowed:
                flash(u'附件上传不允许')
                return redirect(request.args.get('next') or url_for('teacher.teacher_corrected'))
            #可能加入全体广播 向全部学生广播教师修改作业已上传
            flash('上传成功')
            return redirect(url_for('teacher.teacher_corrected', form=form))
    return render_template('teacher/upload_corrected.html', form=form)


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


@teacher.route('/teacher/<course_id>/givegrade_team/<homework_id>', methods=['GET', 'POST'])
def givegrade_teacher(course_id, homework_id): # TODO：完成老师给分
    #显示学生已提交的作业，显示附件
    submission = Submission.query.filter_by(homework_id=homework_id).filter_by(commit_status=1).all()
    homework_list = []
    for i in submission:
        attachment = Attachment.query.filter_by(submission_id=submission.id)

        homework_list.append({'team_id': i.team_id, 'text_content': i.text_content,
                              'grade': i.grade, 'comments': i.comments})
    request.args.get('team_id')
    # 提交评价和评分
    if request.method == 'POST' and request.args.get('action') == 'submit':
        pass
    # 单个下载学生作业
    if request.method == 'POST' and request.args.get('action') == 'download':
        pass
    # 批量下载学生作业
    if request.method == 'POST' and request.args.get('action') == 'multi_download':
        pass
    # for i in homework_list:
    #     #一次提交一个分数与评论
    #     if request.args.get('action') == 'submit':
    #         if form.validate_on_submit():
    #             i['grade'] = form.grade.data
    #             i['comments'] = form.comments.data
    #             submission_1 = submission.query.filter_by(team_id=i['team_id'])
    #             submission_1.grade = form.grade.data
    #             submission_1.comments = form.comments.data
    #             db.session.add(submission_1)
    #             db.session.commit()
    #             return redirect(request.args.get('next') or url_for('teacher/homework/givegrade_tea.html'))
    #         #评论或者分数为空
    #         else:
    #             flash('请输入分数以及评论', 'danger')
    #             return redirect(url_for('teacher/homework/givegrade_tea.html'))
    #     #单个作业下载
    #     else:
    #         if request.args.get('action') == 'download':
    #             # 文件是否存在 attachment_url不确定是不是对的
    #             if os.path.isfile(os.path.join(os.getcwd(), 'uploads', str(i['attachment_url']))):
    #                 response = make_response(send_file(os.path.join(os.getcwd(), 'uploads', str(i['attachment_url']))))
    #             else:
    #                 flash('选择的文件不存在')
    #                 return redirect(url_for('index'))
    #             response.headers["Content-Disposition"] = "attachment; filename=" + str(i['attachment_url']) + ";"
    #             return response
    # #打包下载
    # if request.form.get('action') == 'multidownload':
    #     filelist = request.args.get('filelist')
    #     output_filename = request.args.get('output_filename')
    #     zipf = zipfile.ZipFile(output_filename, 'w')
    #     [zipf.write(filename, filename.rsplit(os.path.sep, 1)[-1]) for filename in filelist]
    #     zipf.close()
    #     response = make_response(send_file(os.path.join(os.getcwd(), output_filename)))
    #     response.headers["Content-Disposition"] = "attachment; filename=" + output_filename + ";"
    #     return response
    return render_template('teacher/homework/givegrade_tea.html', homework_list=homework_list)
