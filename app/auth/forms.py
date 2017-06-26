from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    identity = RadioField('类型', choices=[(0, '教务'), (1, '教师'), (2, '学生')], default=2, validators=[DataRequired()])
    remember_me = BooleanField('记住我')
