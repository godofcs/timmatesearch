from wtforms import StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class ChatsForm(FlaskForm):
    message = StringField('message', validators=[DataRequired()])
    send = SubmitField('send')
