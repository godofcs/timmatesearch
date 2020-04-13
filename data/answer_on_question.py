from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
import datetime
import sqlalchemy
from wtforms.validators import DataRequired


class Answer_on_question(FlaskForm):
    answer = StringField('A n s w e r:', validators=[DataRequired()])
    submit = SubmitField('G o !')
