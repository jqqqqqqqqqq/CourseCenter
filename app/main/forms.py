from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, IntegerField, \
    FileField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Length, InputRequired
from flask_uploads import UploadSet

ups = UploadSet('files', extensions=('xls', 'xlsx'))
homework_ups = UploadSet('files', extensions=('txt', 'doc', 'docx'))  # 暂时只允许提交三种作业文件


class SemesterForm(FlaskForm):
    id = IntegerField('学期ID', validators=[DataRequired()])
    base_info = TextAreaField('学期基本信息', validators=[])
    begin_time = DateField('开始周', validators=[DataRequired()])
    end_time = DateField('结束周', validators=[DataRequired()])


class CourseForm(FlaskForm):
    # teacherTeam_id = IntegerField('教师团队ID', validators=[DataRequired()])
    semester = SelectField(' 学期', choices=[], validators=[InputRequired()], coerce=int)
    name = StringField('课程名称', validators=[InputRequired()])
    course_info = TextAreaField('课程基本信息', validators=[])
    place = StringField('地点', validators=[Length(0, 50)])
    outline = TextAreaField('课程大纲', validators=[InputRequired()])
    credit = IntegerField('学分', validators=[DataRequired()])
    teamsize = IntegerField('课程人数', validators=[DataRequired()])
    stuff_info = FileField('学生老师信息', validators=[
            FileAllowed(ups, u'只接受xls(或xlsx)文件!'),
            FileRequired(u'文件未选择!')])


class AddSemesterForm(FlaskForm):
    id = IntegerField('学期', validators=[DataRequired()])
    base_info = TextAreaField('学期基本信息')
    time = StringField('学期时间', validators=[DataRequired()])


class UploadForm(FlaskForm):
    up = FileField(validators=[
            FileAllowed(ups, u'只接受xls(或xlsx)文件!'),
            FileRequired(u'文件未选择!')])
    submit = SubmitField(u'上传')


class HomeworkForm(FlaskForm):
    text = TextAreaField('作业')
    homework_up = FileField(validators=[
        FileAllowed(homework_ups, u'只接受txt和doc(docx)文件!')])
