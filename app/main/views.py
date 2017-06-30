from flask import render_template, redirect, url_for, flash, request, session
from . import main
from .. import db
import os
from .forms import  upsr, UploadResourceForm
from ..models.models import SCRelationship, TCRelationship, Course
from flask_login import current_user, login_required
from flask import request
from config import basedir
from flask_uploads import UploadNotAllowed
import uuid


@main.before_request
@login_required
def before_request():
    pass


@main.route('/', methods=['GET', 'POST'])
def index():

    #教师特色主页
    if current_user.user_type() == 1:
        tcrels = TCRelationship.query.filter_by(teacher_id=current_user.id).all()
        courses = []
        for rel in tcrels:
            courses.append(Course.query.filter_by(id=rel.course_id).first())
        return render_template('teacher/index.html', courses=courses)

    # 学生特色主页
    if current_user.user_type() == 2:
        tcrels = SCRelationship.query.filter_by(student_id=current_user.id).all()
        courses = []
        for rel in tcrels:
            courses.append(Course.query.filter_by(id=rel.course_id).first())
        return render_template('student/index.html', courses=courses)

    return render_template('index.html')


@main.route('/uploadresource', methods=['GET', 'POST'])
def teacher_resource():
    form = UploadResourceForm()
    if form.validate_on_submit():
        try:
            (name, ext) = os.path.splitext(form.up.data.filename)
            #print(ext)
            filename = upsr.save(form.up.data, basedir + '/uploads/teacher_resources', name=str(uuid.uuid4())+'.'+ext)
            file_url = upsr.url(filename)
        except UploadNotAllowed:
            flash('附件上传不允许！', 'danger')
            return redirect(request.args.get('next') or url_for('uploadresource.html'))
    else:
        file_url = None
    return render_template('uploadresource.html', form=form, file_url=file_url)
