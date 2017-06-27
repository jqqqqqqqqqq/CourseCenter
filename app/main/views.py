from flask import render_template, redirect, url_for, request
from . import main
from .forms import CourseForm



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


@main.route('/set-course-info')
def set_course_info():
    form = CourseForm()
    form.teamsize.data = 1
    if form.validate_on_submit():
        print(form.course_info.data)
        return redirect(request.args.get('next') or url_for(''))
    return render_template('set_course_info.html', form=form)
