from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, SubmitField, BooleanField,SelectField,TextAreaField,FloatField,DateField,IntegerField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    identity = RadioField('类型', choices=[('0', '教务'), ('1', '教师'), ('2', '学生')], default='2', validators=[DataRequired()])
    remember_me = BooleanField('记住我',default=False)

class Semester_Info_Form(FlaskForm):
    id = IntegerField('学期ID', validators=[DataRequired()])
    base_info = TextAreaField('学期基本信息',validators=[])
    begin_time = DateField('开始周', validators=[DataRequired()])
    end_time = DateField('结束周', validators=[DataRequired()])

class Course_Info_Form(FlaskForm):
    id = IntegerField('课程ID', validators=[DataRequired()])
    teacherTeam_id = IntegerField('教师团队ID', validators=[DataRequired()])
    semester_id = IntegerField('学期ID', validators=[DataRequired()])
    course_info = TextAreaField('课程基本信息',validators=[])
    place = StringField('地点',validators=[len(0,50)])
    outline = TextAreaField('课程大纲',validators=[])
    credit = IntegerField('学分',validators=[DataRequired()])
    teamsize = IntegerField('课程人数',validators=[DataRequired()])