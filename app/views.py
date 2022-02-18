from flask import render_template, flash, request, redirect, url_for
from app import app
from .forms import UserForm
from .models import User
from app import db
import datetime

# Home view
@app.route('/', methods=['GET', 'POST'])
def home():
	home={'description':'Welcome.'}
	return render_template('home.html',
						   title='Home',home=home)

# View when on the add users page
@app.route('/add', methods=['GET', 'POST'])
def addA():
    form = UserForm()
    if form.validate_on_submit():
        # gets all the inputs from the user to store into database
        nuser=request.form.get("username")
        npassword=request.form.get("password")
        # stores data into database
        new_user = User(username = nuser,password=npassword)
        db.session.add(new_user)
        db.session.commit()
        flash("User added")
        # returns user back to add users page once form is submitted to clear all the form's input boxes
        return redirect(url_for("addA"))

    return render_template('add.html',
                           title='Add User',
                           form=form)

# View for viewing all users
# Passes all the users stored in the database to users.html to be outputted
@app.route('/users', methods=['GET', 'POST'])
def users():
    users = User.query.all()

    return render_template('users.html',
						    title='Users',users=users)
