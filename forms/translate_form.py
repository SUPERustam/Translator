from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy import orm


class TranslateForm(FlaskForm):
    content = TextAreaField("Русский язык", validators=[DataRequired()])
    submit = SubmitField("Перевод")