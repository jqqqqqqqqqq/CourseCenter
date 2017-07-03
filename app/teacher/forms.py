from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, StringField, SubmitField
from wtforms.validators import InputRequired, DataRequired, NumberRange
from flask_uploads import UploadSet
from flask_wtf.file import FileField, FileAllowed, FileRequired

upsr = UploadSet('files', extensions=('xls', 'xlsx', 'pdf', 'doc', 'docx', 'txt', 'zip', '7z', 'rar'))
up_corrected = UploadSet('files', extensions=('zip', 'rar'))


class CourseForm(FlaskForm):
    outline = TextAreaField('课程大纲', validators=[InputRequired()])
    teamsize_max = IntegerField('课程人数上限', validators=[DataRequired()])
    teamsize_min = IntegerField('课程人数下限', validators=[DataRequired()])


class HomeworkForm(FlaskForm):
    name = StringField('作业名', validators=[DataRequired()])
    base_requirement = TextAreaField('作业要求', validators=[DataRequired()])
    time = StringField('持续时间', validators=[DataRequired()])
    weight = IntegerField('权重', validators=[DataRequired(), NumberRange(min=1, max=100, message='权重需要在1-100之间')])
    max_submit_attempts = IntegerField('最大提交次数', validators=[DataRequired()])


class UploadResourceForm(FlaskForm):
    up = FileField(validators=[
        FileAllowed(upsr, u'xls, xlsx, pdf, doc, docx, txt, zip, 7z, rar'),
        FileRequired(u'文件未选择!')])
    submit = SubmitField(u'上传')


class UploadCorrected(FlaskForm):
    up_corrected = FileField(validators=[FileAllowed(up_corrected, u'zip and rar only'),
                                         FileRequired(u'文件未选择!')])
    submit = SubmitField(u'上传')


class AcceptTeam(FlaskForm):
    id = IntegerField(validators=[InputRequired()])
    # button = SubmitField('通过')


class RejectTeam(FlaskForm):
    id = IntegerField(validators=[InputRequired()])
    # button = SubmitField('拒绝')
    reason = TextAreaField('拒绝理由', validators=[InputRequired()])
