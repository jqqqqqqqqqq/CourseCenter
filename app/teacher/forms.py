from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, StringField, SubmitField, SelectField
from wtforms.validators import InputRequired, DataRequired, NumberRange, ValidationError
from flask_uploads import UploadSet
from flask_wtf.file import FileField, FileAllowed, FileRequired

upsr = UploadSet('files', extensions=('xls', 'xlsx', 'pdf', 'doc', 'docx', 'txt', 'zip', '7z', 'rar'))
up_corrected = UploadSet('files', extensions=('zip', 'rar'))


class CourseForm(FlaskForm):
    outline = TextAreaField('课程大纲', validators=[InputRequired()])
    teamsize_max = IntegerField('课程人数上限', validators=[DataRequired(), NumberRange(min=1, message='至少需要一个人')])
    teamsize_min = IntegerField('课程人数下限', validators=[DataRequired(), NumberRange(min=1, message='至少需要一个人')])

    def validate(self):
        if not super(CourseForm, self).validate():
            return False
        if not self.teamsize_min.data <= self.teamsize_max.data:
            self.teamsize_min.errors.append('下限人数不多于上限')
            self.teamsize_max.errors.append('上限人数不少于下限')
            return False
        return True


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


class MoveForm(FlaskForm):
    student = IntegerField('学生id', validators=[DataRequired()])
    pending_teams = SelectField('可以加入的组',
                                choices=[],
                                coerce=int)
