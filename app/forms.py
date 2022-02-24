from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, EmailField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError
from flask import flash
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



class PaymentForm(FlaskForm):

    cardNum = StringField('Card number', validators=[DataRequired(), validators.length(min=16, max=16)])
    expiration = StringField('Expiration date', validators=[DataRequired(), validators.length(min=3, max=4)])
    securityNum = PasswordField('Security code', validators=[DataRequired(), validators.length(min=3, max=3)])
    submit = SubmitField('Purchase')

    #custom validator for cardNum
    def validate_cardNum(form, field):
        if (not field.data.isdigit()):
            flash("Card number must be a number")
            raise ValidationError()
    
    #custom validator for expiration date
    def validate_expiration(form, field):
        if (not field.data.isdigit()):
            flash("Expiration date must be a number")
            raise ValidationError()

    #custom validator for security num
    def validate_securityNum(form, field):
        if (not field.data.isdigit()):
            flash("Security number must be a number")
            raise ValidationError()

