from wtforms import StringField, PasswordField, SubmitField, FileField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class EditProfileForm(FlaskForm):
    old_password = PasswordField('Old password')
    new_password = PasswordField('New password')
    new_password_again = PasswordField('Repeat the new password')
    name = StringField('Nickname', validators=[DataRequired()])
    avatar = FileField("Avatar")
    favorite_games = StringField('Favorite games')
    submit = SubmitField('edit')
    submit_rus = SubmitField('изменить')
