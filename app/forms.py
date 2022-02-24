from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, EmailField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), validators.length(min=8)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class ScooterForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])

class OptionsForm(FlaskForm):
    hours = IntegerField('hours', validators=[DataRequired()])
    price = IntegerField('price', validators=[DataRequired()])
