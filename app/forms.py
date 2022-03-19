from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, EmailField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError
from flask import flash



#start of our custom validators

#custom validator, which checks the input string to see if it is an integer
def checkForNum(form, field):
    if (not field.data.isdigit()):
        raise ValidationError('Must be a number')

#custom validator, which checks that the string contains at least one special character
def checkForSpecialChar(form, field):
    foundChar = False
    characters = """!"#$%&'()*+,-./:;<=>?@[\]^_`{"""# a string composing of every special character
    for i in field.data:#iterate over each character in our input
        for j in characters:#for each char in field iterate over the special characters
            if (i == j):#if we have found one that matches
                foundChar = True
                break#stop the loop

    if (not foundChar):
        raise ValidationError('Must contain at least one special character')

#custom validator similair to checkForSpecialChar, which checks that the input has at least 1 number
def checkForPassNumber(form, field):
    foundInt = False
    for i in field.data:#iterate over each character in our input
        if(i.isdigit()):#if it is a number
            foundInt = True
            break#stop the loop

    if (not foundInt):
        raise ValidationError('Must contain at least one number')

#end of our custom validators



class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), validators.length(min=8), checkForSpecialChar, checkForPassNumber])
    student = BooleanField('Are you a student?')
    seniorCitizen = BooleanField('Are you a senior citizen?')
    submit = SubmitField('Register')

class RegisterManagerForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), validators.length(min=8),  checkForSpecialChar, checkForPassNumber])
    managerPassword = PasswordField('Managerpassword', validators=[DataRequired()])
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

class AddPaymentMethodForm(FlaskForm):
    cardNum = StringField('Card Number', validators=[DataRequired(), validators.length(min=16, max=16), checkForNum])
    expiryDate = StringField('expiryDate', validators=[DataRequired(), validators.length(min=3, max=4), checkForNum])
    cardName = StringField('cardName', validators=[DataRequired()])
    submit = SubmitField('Add Payment Detail')

class PaymentForm(FlaskForm):
    cardNum = StringField('Card number', validators=[DataRequired(), validators.length(min=16, max=16), checkForNum])
    expiration = StringField('Expiration date', validators=[DataRequired(), validators.length(min=3, max=4), checkForNum])
    securityNum = PasswordField('Security code', validators=[DataRequired(), validators.length(min=3, max=3), checkForNum])
    submit = SubmitField('Purchase')

class FeedbackForm(FlaskForm):
    scooterId = StringField('ScooterId', validators=[DataRequired()])
    feedback = StringField('feedback', validators=[DataRequired()])
    submit = SubmitField('Send Feedback')
