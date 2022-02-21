from flask import render_template, flash, request, redirect, url_for
from app import app
from .forms import RegisterForm
from .models import Customer
from app import db


# Home view
@app.route('/', methods=['GET', 'POST'])
def index():
	home={'description':'Welcome.'}
	return render_template('home.html', title='Home', home=home)

# Register view
@app.route('/register', methods=['GET', 'POST'])
def register():
	username = None
	password = None
	form = RegisterForm()

	return render_template('register.html', title='Register', username=username, password=password, form=form)