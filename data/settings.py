from wtforms import StringField, SubmitField, BooleanField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class Settings_form(FlaskForm):
    white_theme = SubmitField('White theme')
    dusty_cheese_theme = SubmitField('Dusty cheese theme')  # beige
    sneezing_fairy_theme = SubmitField('Sneezing fairy theme')  # #e3f3ff
    lilac_cloud_theme = SubmitField('lilac cloud theme')  # #f9e8fa
    ru_language = SubmitField('Russian language')
    en_language = SubmitField('English language')
