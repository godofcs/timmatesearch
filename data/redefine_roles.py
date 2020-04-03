from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class Redefine_role(FlaskForm):
    user_id = StringField('user id', validators=[DataRequired()])
    input_user_role = StringField()
    submit = SubmitField('search')
    save = SubmitField('save')
