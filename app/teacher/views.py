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
import json
from openpyxl import Workbook


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
                return redirect(url_for('teacher.manage_resource', course_id=course_id, path=path))
            if os.path.isfile(filepath):
                os.remove(filepath)
            else:
                shutil.rmtree(filepath)
            flash('删除成功！', 'success')
            return redirect(url_for('teacher.manage_resource', course_id=course_id, path=path))

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

    files = list(os.scandir(expand_path))
    return render_template('teacher/resource.html', course_id=course_id, files=files, path=path)


@teacher.route('/<course_id>/homework', methods=['GET', 'POST'])
@UserAuth.teacher_course_access
def homework(course_id):

    form = HomeworkForm()
    if form.validate_on_submit():
        begin_time, end_time = form.time.data.split(' - ')
        begin_time = datetime.strptime(begin_time, '%m/%d/%Y %H:%M')
        end_time = datetime.strptime(end_time, '%m/%d/%Y %H:%M')

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

        flash('发布成功！', 'success')
        return redirect(url_for('teacher.homework', course_id=course_id))
    course = Course.query.filter_by(id=course_id).first()

    homework_list = Homework.query.filter_by(course_id=course_id).all()
    return render_template('teacher/homework.html', course_id=course_id, homeworks=homework_list, form=form, course=course)


@teacher.route('/<course_id>/homework/<homework_id>', methods=['GET', 'POST'])
@UserAuth.teacher_course_access
def homework_detail(course_id, homework_id):
    # 作业详情
    form = HomeworkForm()
    course = Course.query.filter_by(id=course_id).first()
    homework = Homework.query.filter_by(id=homework_id).first()
    if form.validate_on_submit():
        # 修改作业
        begin_time, end_time = form.time.data.split(' - ')
        begin_time = datetime.strptime(begin_time, '%m/%d/%Y %H:%M')
        end_time = datetime.strptime(end_time, '%m/%d/%Y %H:%M')

        homework.name = form.name.data
        homework.base_requirement = form.base_requirement.data
        homework.begin_time = begin_time
        homework.end_time = end_time
        homework.weight = form.weight.data
        homework.max_submit_attempts = form.max_submit_attempts.data
        homework.course_id = course_id

        flash('修改成功！', 'success')
        return redirect(url_for('teacher.homework_detail',
                                course_id=course_id,
                                homework_id=homework_id))

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


# PudgeG负责：得到本次作业报表↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
def get_homework_report(homework_id):
    # 得到本次作业报表
    submission_list = Submission.query.filter_by(homework_id=homework_id).all()
    homework = Homework.query.filter_by(id=request.args.get('homework_id')).first()
    team_this_course = Team.query.filter_by(course_id=homework.course_id).filter_by(status=2).all()
    Team.team_list(homework.course_id)
    if submission_list is None:
        flash('无提交记录，请先催交！', 'danger')
        return redirect(request.args.get('next') or url_for('main.set_homework'))
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = homework.name + ' 提交情况'
    worksheet.append(['团队名称', '团队ID', '本次作业是否提交', '本次作业分数'])
    input_info = []
    i = 0
    for team in team_this_course:
        finished = Submission.query.filter_by(homework_id=homework_id).filter_by(team_id=team.id).first()

        def convert_status(status):
            switcher = {
                0: '作业未批改',
                1: '作业已批改'
            }
            return switcher.get(status, '其他')

        if Submission.query.filter_by(team_id=team.id).first():
        homework_record = {'团队名称': team.team_name,
                        '团队ID': team.order,
                        '本次作业是否提交': convert_status(team.status),
                        '本次作业分数': finished.score}
        input_info.append(homework_record)
    worksheet.append(input_info)
    worksheet.save('homework_report.xlsx')
    if os.path.isfile(os.path.join(os.getcwd(), 'homework', 'homework_report.xlsx')):
        response = make_response(send_file(os.path.join(os.getcwd(), 'homework', 'homework_report.xlsx')))
    else:
        flash('文件创建失败！', 'danger')
        return redirect(url_for('teacher/teacher_teammanagement'))
    response.headers["Content-Disposition"] = "attachment; filename=" + 'homework_report.xlsx' + ";"
    return response
# PudgeG负责：得到本次作业报表↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑



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


def add_member(student_id, team_id):
    team_member = TeamMember()
    team_member.team_id = team_id
    team_member.student_id = student_id
    team_member.status = 0
    db.session.add(team_member)
    delete_list = TeamMember.query.filter_by(status=2).filter_by(student_id=student_id).all()
    for a in delete_list:
        db.session.delete(a)
    db.session.commit()


@teacher.route('/index-teacher/<course_id>/teacher-teammanagement', methods=['GET', 'POST'])
def teacher_teammanagement(course_id):
    if 'accept' in request.form.values():
        form = AcceptTeam()
        _team = Team.query.filter_by(id=int(form.id.data)).first()
        if _team:
            _team.status = 1  # 1是通过
            db.session.add(_team)
            db.session.commit()
            flash('通过成功', 'success')
            return redirect(request.args.get('next') or url_for('main.teacher_teammanagement'))
        else:
            flash('找不到此团队', 'danger')
            return redirect(request.args.get('next') or url_for('main.teacher_teammanagement'))
    elif 'reject' in request.form.values():
        form = RejectTeam()
        _team = Team.query.filter_by(id=int(form.id.data)).first()
        if _team:
            _team.status = 2  # 2是拒绝
            _team.reason = form.reason.data
            db.session.add(_team)
            db.session.commit()
            flash('拒绝成功', 'success')
            return redirect(request.args.get('next') or url_for('main.teacher_teammanagement'))
        else:
            flash('找不到此团队', 'danger')
            return redirect(request.args.get('next') or url_for('main.teacher_teammanagement'))

    # PudgeG负责:团队报表导出↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    elif 'teamtable' in request.form.values():
        down_list = Team.query.filter_by(course_id=course_id).all()
        if down_list is None:
            flash('没有团队，请等待申请并批准！', 'danger')
            return redirect(request.args.get('next') or url_for('main.teacher_teammanagement'))
        else:
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = '团队信息'
            worksheet.append(['team_name', 'team_id', 'member_name', 'member_id', 'member_role'])
            # i = 0 表示队伍数量
            input_info = []
            for ateam in down_list:
                member_list = TeamMember.query.filter_by(team_id=ateam.id).all()
                input_list = {'team_name': ateam.team_name,
                              'team_id': ateam.id,
                              'member_name': Student.query.filter_by(id=ateam.owner_id).name,
                              'member_id': ateam.owner_id,
                              'member_role': 'manager'}
                input_info.append(input_list)
                # num_of_member = len(member_list)+1 表示每支队伍人员数量
                # i += 1
                for aaa in member_list:
                    input_list = {'team_name': ateam.team_name,
                                  'team_id': ateam.id,
                                  'member_name': Student.query.filter_by(id=aaa.student_id).name,
                                  'member_id': aaa.student_id,
                                  'member_role': 'member'}
                    input_info.append(input_list)
            worksheet.append(input_info)
            worksheet.save('team_table.xlsx')
            if os.path.isfile(os.path.join(os.getcwd(), 'team_manage', 'team_table.xlsx')):
                response = make_response(send_file(os.path.join(os.getcwd(), 'team_manage', 'team_table.xlsx')))
            else:
                flash('文件创建失败！', 'danger')
                return redirect(url_for('teacher/teacher_teammanagement'))
            response.headers["Content-Disposition"] = "attachment; filename=" + 'team_table.xlsx' + ";"
            return response
        # PudgeG负责:团队报表输出↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

    _team_list = Team.query.all()

    class TeamList:
        id = 0
        status = 0
        team_name = ''

        def __init__(self, id, status, team_name):
            self.id = id
            self.status = status
            self.team_name = team_name

    team_list = [TeamList(a.id, a.status, a.team_name) for a in _team_list]
    for team in team_list:
        _team_members = TeamMember.query.filter_by(team_id=team.id).all()
        member_name = ''
        for member in _team_members:
            real_name = Student.query.filter_by(id=member.student_id).first().name
            member_name += member.team_name + '(' + real_name + '), '
        team.member_name = member_name  # 把所有人名字构造成一个字符串
        team.accept_form = AcceptTeam()
        team.accept_form.id.data = team.id
        team.reject_form = RejectTeam()
        team.reject_form.id.data = team.id
    return render_template('auth_teacher/teacher_teammanagement.html',
                           team_list=team_list)


@teacher.route('/teacher/<course_id>/givegrade_team/<homework_id>', methods=['GET', 'POST'])
def givegrade_teacher(course_id, homework_id):
    # 显示学生已提交的作业(显示最新的提交记录)
    submission = Submission.query.filter_by(homework_id=homework_id).filter_by(submit_status=1).all()
    homework_list = []
    for i in submission:
        team = Team.query.filter_by(id=i.team_id).first()
        homework_list.append({'team_id': i.team_id, 'team_name': team.team_name, 'text_content': i.text_content,
                              'score': i.score, 'comments': i.comments})

    # json [{'team_id':team_id, 'score': score, 'comments': comments}]
    # 提交评价和评论
    if request.method == 'POST' and request.form.get('action') == 'submit':
        _list = json.loads(request.form.get('data'))
        for dic in _list:
            for submission_temp in submission:
                if submission_temp.team_id == dic['team_id']:
                    submission_temp.score = dic['score']
                    submission_temp.comments = dic['comments']
                    db.session.add(submission_temp)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('teacher.givegrade_teacher', homework_list=homework_list))

    # 单个下载学生作业
    if request.method == 'POST' and request.form.get('action') == 'download':
        team_id = request.form.get('team_id')
        file_dir = os.path.join(current_app.config['UPLOADED_FILES_DEST'],
                                str(course_id),
                                str(homework_id),
                                str(team_id))
        # 取最新的一次上传和上传时的附件
        submission_temp = submission.query.filter_by(team_id=int(team_id)).filter_by(submit_status=1).first()
        attachment_temp = Attachment.query.filter_by(submission_id=submission_temp.id).first()
        filename_upload = attachment_temp.file_name
        file_uuid = attachment_temp.guid

        # 寻找保存目录下的uuid文件
        for i in os.listdir(file_dir):
            if i.startswith(str(file_uuid)):
                os.rename(i, filename_upload)

        # 无附件
        if not attachment_temp:
            flash('该组没有上传作业')
            return redirect(url_for('teacher.givegrade_teacher', homework_list=homework_list))
        elif os.path.exists(os.path.join(file_dir, filename_upload)):
            return send_from_directory(file_dir, filename_upload, as_attachment=True)
    # 批量下载学生作业
    if request.method == 'POST' and request.form.get('action') == 'multi_download':
        file_path = os.path.join(basedir, 'uploads', str(course_id), str(homework_id))

        return send_from_directory()
    # if request.form.get('action') == 'multidownload':
    #     filelist = request.args.get('filelist')
    #     output_filename = request.args.get('output_filename')
    #     zipf = zipfile.ZipFile(output_filename, 'w')
    #     [zipf.write(filename, filename.rsplit(os.path.sep, 1)[-1]) for filename in filelist]
    #     zipf.close()
    #     response = make_response(send_file(os.path.join(os.getcwd(), output_filename)))
    #     response.headers['Content-Disposition'] = 'attachment; filename=' + output_filename + ';'
    #     return response
    return render_template('teacher/homework/givegrade_teacher.html', homework_list=homework_list)


def make_zip(source_dir, output_filename):
  zipf = zipfile.ZipFile(output_filename, 'w')
  pre_len = len(os.path.dirname(source_dir))
  for parent, dirnames, filenames in os.walk(source_dir):
    for filename in filenames:
      pathfile = os.path.join(parent, filename)
      arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
      zipf.write(pathfile, arcname)
  zipf.close()