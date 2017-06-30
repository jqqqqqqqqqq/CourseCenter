from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, StringField
from wtforms.validators import InputRequired, DataRequired


class CourseForm(FlaskForm):
    outline = TextAreaField('课程大纲', validators=[InputRequired()])
    teamsize_max = IntegerField('课程人数上限', validators=[DataRequired()])
    teamsize_min = IntegerField('课程人数下限', validators=[DataRequired()])


class HomeworkForm(FlaskForm):
    name = StringField('作业名', validators=[DataRequired()])
    base_requirement = TextAreaField('作业要求', validators=[DataRequired()])
    time = StringField('持续时间', validators=[DataRequired()])
    weight = IntegerField('权重', validators=[DataRequired()])
    max_submit_attempts = IntegerField('最大提交次数', validators=[DataRequired()])
