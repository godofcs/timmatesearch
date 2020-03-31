from wtforms import StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    password_again = PasswordField('repeat the password', validators=[DataRequired()])
    about = StringField('About you', validators=[DataRequired()])
    name = StringField('nickname', validators=[DataRequired()])
    submit = SubmitField('login')
