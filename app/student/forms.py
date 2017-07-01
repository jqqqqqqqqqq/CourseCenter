from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, IntegerField
from wtforms.validators import DataRequired, InputRequired, Length
from flask_uploads import UploadSet

homework_ups = UploadSet('files', extensions=('txt', 'doc', 'docx'))   # 只允许提交三种作业文件 提交作业ups


class HomeworkForm(FlaskForm):
    text = TextAreaField('作业')
    homework_up = FileField(validators=[
        FileAllowed(homework_ups, u'只接受txt和doc(docx)文件!')])


class CreateTeamForm(FlaskForm):
    owner_id = IntegerField('团队负责人', validators=[DataRequired()])
    team_name = TextAreaField('团队名称', validators=[DataRequired()])
    status = IntegerField('队伍状态')
    course_id = IntegerField('所属课程', validators=[DataRequired()])
    rejection_reason = TextAreaField('拒绝理由')
