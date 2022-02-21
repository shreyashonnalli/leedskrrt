from flask_wtf import Form
from wtforms import validators
from wtforms.fields import EmailField, PasswordField
from wtforms.validators import DataRequired


class RegisterForm(Form):
    username = EmailField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
