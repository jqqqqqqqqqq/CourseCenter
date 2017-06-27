from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, DateField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length
from ..models.models import Semester


class EditSemesterForm(FlaskForm):
    id = IntegerField('学期', validators=[DataRequired()])
    base_info = TextAreaField('学期基本信息')
    time = StringField('学期时间', validators=[DataRequired()])
