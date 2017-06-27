from flask import render_template, redirect, url_for
from . import main
from .forms import EditSemesterForm
from flask_login import login_required, current_user
from .. import db
from ..models.models import Semester
import datetime


@main.route('/', methods=['GET', 'POST'])
def index():
    # return redirect(url_for('auth.login'))
    return render_template('index.html')


@main.route('/manage-semester', methods=['GET', 'POST'])
def manage_semester():
    form = EditSemesterForm()
    id = int(form.id.data)
    base_info = form.base_info.data
    time = form.time.data
    begin_time, end_time = time.split('-')
    start_time = datetime.datetime.strptime(begin_time, '%m/%d/%Y')
    finish_time = datetime.datetime.strptime(end_time, '%m/%d/%Y')
    if form.validate_on_submit():
        semester = Semester(id=id, base_info=base_info, begin_time=start_time, end_time=finish_time)
        db.session.add(semester)
        return redirect('.manage-semester')
    form.id.data = id
    form.base_info.data = base_info
    form.time.data = time
    return render_template('manage_semester.html', form=form)


@main.route('/manage-course')
def manage_course():
    return render_template('manage_course.html')
