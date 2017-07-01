from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, IntegerField, StringField
from wtforms.validators import DataRequired, InputRequired, Length
from flask_uploads import UploadSet

homework_ups = UploadSet('files', extensions=('txt', 'doc', 'docx'))   # 只允许提交三种作业文件 提交作业ups


class HomeworkForm(FlaskForm):
    text = TextAreaField('作业')
    homework_up = FileField(validators=[
        FileAllowed(homework_ups, u'只接受txt和doc(docx)文件!')])


class CreateTeamForm(FlaskForm):
    team_name = StringField('团队名称', validators=[DataRequired()])
    status = IntegerField('队伍状态')


class MemberForm(FlaskForm):
    member_id = IntegerField(validators=[InputRequired])


class EditTeam(FlaskForm):
    new_name = StringField('队伍名称', validators=[DataRequired()])
