from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,  DateField, SubmitField, IntegerField, \
    FileField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, InputRequired
from flask_uploads import UploadSet

upsr = UploadSet('files', extensions=('xls', 'xlsx', 'pdf', 'doc', 'docx', 'txt', 'zip', '7z', 'rar'))


class UploadResourceForm(FlaskForm):
    up = FileField(validators=[
        FileAllowed(upsr, u'xls, xlsx, pdf, doc, docx, txt, zip, 7z, rar'),
        FileRequired(u'文件未选择!')])
    submit = SubmitField(u'上传')
