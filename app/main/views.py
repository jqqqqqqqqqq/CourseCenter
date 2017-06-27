from flask import render_template, redirect, url_for, request
from . import main
from .forms import CourseForm
from app.models import models

this_term = 1


@main.route('/', methods=['GET', 'POST'])
def index():
    # return redirect(url_for('auth.login'))
    return render_template('index.html')


@main.route('/manage-semester')
def manage_semester():
    return render_template('manage_semester.html')


@main.route('/manage-course')
def manage_course():
    return render_template('manage_course.html')


@main.route('/set-course-info', methods=['GET', 'POST'])
def set_course_info():
    form = CourseForm()
    course = models.Course.query.filter_by(id=this_term).first()
    form.course_info.data = course.course_info
    form.place.data = course.place
    form.outline.data = course.outline
    form.credit.data = course.credit
    form.teamsize.data = course.teamsize
    if form.validate_on_submit():
        print(form.course_info.data)
        return redirect(request.args.get('next') or url_for('main.set_course_info'))
    return render_template('set_course_info.html', form=form)
