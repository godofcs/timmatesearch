from wtforms import StringField, SubmitField, TextAreaField
from flask_wtf import FlaskForm
import datetime
import sqlalchemy
from wtforms.validators import DataRequired


class Answer_on_question(FlaskForm):
    answer = TextAreaField('A n s w e r:', validators=[DataRequired()])
    submit = SubmitField('G o !')
    submit_rus = SubmitField('В п е р ё д !')
