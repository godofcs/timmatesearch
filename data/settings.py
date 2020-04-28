from wtforms import StringField, SubmitField, BooleanField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class Settings_form(FlaskForm):
    white_theme = SubmitField('White theme')
    white_theme_rus = SubmitField('Белая тема')
    dusty_cheese_theme = SubmitField('Dusty cheese theme')  # beige
    dusty_cheese_theme_rus = SubmitField('Тема "Пыльный сыр"')  # beige
    sneezing_fairy_theme = SubmitField('Sneezing fairy theme')  # #e3f3ff
    sneezing_fairy_theme_rus = SubmitField('Тема "Чихание феечки"')  # #e3f3ff
    lilac_cloud_theme = SubmitField('lilac cloud theme')  # #f9e8fa
    lilac_cloud_theme_rus = SubmitField('Тема "Сиреневое облако"')  # #f9e8fa
    ru_language = SubmitField('Русский')
    en_language = SubmitField('English language')
