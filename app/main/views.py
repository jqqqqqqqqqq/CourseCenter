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
    semester_list = Semester.query.all()
    res = []
    for semester in semester_list:
        res.append({'id': semester.id,
                    'base_info': semester.base_info,
                    'time': semester.begin_time + '-' + semester.end_time})
    return render_template('manage_semester.html', res=res)


@main.route('/manage-course')
def manage_course():
    return render_template('manage_course.html')
