from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, IntegerField, \
    FileField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Length, InputRequired
from flask_uploads import UploadSet

ups = UploadSet('files', extensions=('xlsx'))
homework_ups = UploadSet('files', extensions=('txt', 'doc', 'docx'))   # 只允许提交三种作业文件 提交作业ups
upsr = UploadSet('files', extensions=('xls', 'xlsx', 'pdf', 'doc', 'docx', 'txt', 'zip', '7z', 'rar'))


class SemesterForm(FlaskForm):
    id = IntegerField('学期ID', validators=[DataRequired()])
    base_info = TextAreaField('学期基本信息', validators=[])
    begin_time = DateField('开始周', validators=[DataRequired()])
    end_time = DateField('结束周', validators=[DataRequired()])


class CourseForm(FlaskForm):
    semester = SelectField('学期', choices=[], validators=[InputRequired()], coerce=int)
    name = StringField('课程名称', validators=[InputRequired()])
    course_info = TextAreaField('课程基本信息', validators=[])
    place = StringField('地点', validators=[Length(0, 50)])
    credit = IntegerField('学分', validators=[DataRequired()])
    stuff_info = FileField('学生老师信息', validators=[
            FileAllowed(ups, u'只接受xls(或xlsx)文件!'),
            FileRequired(u'文件未选择!')])


class CourseFormTeacher(FlaskForm):
    outline = TextAreaField('课程大纲', validators=[InputRequired()])
    teamsize_max = IntegerField('课程人数上限', validators=[DataRequired()])
    teamsize_min = IntegerField('课程人数下限', validators=[DataRequired()])


class AddSemesterForm(FlaskForm):
    id = IntegerField('学期', validators=[DataRequired()])
    base_info = TextAreaField('学期基本信息')
    time = StringField('学期时间', validators=[DataRequired()])


class HomeworkForm(FlaskForm):
    text = TextAreaField('作业')
    homework_up = FileField(validators=[
        FileAllowed(homework_ups, u'只接受txt和doc(docx)文件!')])


class UploadResourceForm(FlaskForm):
    up = FileField(validators=[
        FileAllowed(upsr, u'xls, xlsx, pdf, doc, docx, txt, zip, 7z, rar'),
        FileRequired(u'文件未选择!')])
    submit = SubmitField(u'上传')


class HomeworkFormTeacher(FlaskForm):
    name = StringField('作业名', validators=[DataRequired()])
    base_requirement = TextAreaField('作业要求', validators=[DataRequired()])
    time = StringField('持续时间', validators=[DataRequired()])
    weight = IntegerField('权重', validators=[DataRequired()])
    max_submit_attempts = IntegerField('最大提交次数', validators=[DataRequired()])