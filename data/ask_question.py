from wtforms import StringField, SubmitField, TextAreaField
from flask_wtf import FlaskForm
import datetime
import sqlalchemy
from wtforms.validators import DataRequired


class Ask_question(FlaskForm):
    title = StringField('T i t l e:', validators=[DataRequired()])
    question = TextAreaField('Q u e s t i o n:', validators=[DataRequired()])
    theme = StringField('T h e m e:', validators=[DataRequired()])
    submit = SubmitField('G o !')
    submit_rus = SubmitField('В п е р ё д !')
