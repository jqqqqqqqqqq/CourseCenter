from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm
from . import auth
from ..models.models import DeanInfo, Student, Teacher


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.identity.data == '0':
            user = DeanInfo.query.filter_by(id=form.username.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
        elif form.identity.data == '1':
            user = Teacher.query.filter_by(id=form.username.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
        else:
            user = Student.query.filter_by(id=form.username.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或账户错误')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
