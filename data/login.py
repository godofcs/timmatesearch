from wtforms import StringField, PasswordField, SubmitField, BooleanField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField('login')
