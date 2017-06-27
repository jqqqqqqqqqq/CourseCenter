from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, DateField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length
# from ..models.models import Semester


class SemesterForm(FlaskForm):
    id = IntegerField('学期ID', validators=[DataRequired()])
    base_info = TextAreaField('学期基本信息', validators=[])
    begin_time = DateField('开始周', validators=[DataRequired()])
    end_time = DateField('结束周', validators=[DataRequired()])


class CourseForm(FlaskForm):
    # id = IntegerField('课程ID', validators=[DataRequired()])
    # teacherTeam_id = IntegerField('教师团队ID', validators=[DataRequired()])
    # semester_id = IntegerField('学期ID', validators=[DataRequired()])
    course_info = TextAreaField('课程基本信息', validators=[])
    place = StringField('地点', validators=[Length(0, 50)])
    outline = TextAreaField('课程大纲', validators=[])
    credit = IntegerField('学分', validators=[DataRequired()])
    teamsize = IntegerField('课程人数', validators=[DataRequired()])


class AddSemesterForm(FlaskForm):
    id = StringField('学期', validators=[DataRequired()])
    base_info = TextAreaField('学期基本信息')
    time = StringField('学期时间', validators=[DataRequired()])

