from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired

class UserForm(Form):
    username = TextField('title', validators=[DataRequired()])
    password = TextField('code', validators=[DataRequired()])
