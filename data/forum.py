from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
import datetime
import sqlalchemy
from wtforms.validators import DataRequired


class Forum(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    question = StringField('question', validators=[DataRequired()])
    theme = StringField('theme', validators=[DataRequired()])
    submit = SubmitField('Go!')
