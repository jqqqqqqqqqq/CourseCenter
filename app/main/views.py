from flask import render_template, redirect, url_for
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    # return redirect(url_for('auth.login'))
    return render_template('index.html')


@main.route('/manage-semester', methods=['GET', 'POST'])
def manage_semester():
    return render_template('manage_semester.html')

