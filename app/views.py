from flask import render_template, flash, request, redirect, url_for, session
from app import app, db, bcrypt
from .forms import RegisterForm, LoginForm, ScooterForm, OptionsForm, PaymentForm, RegisterManagerForm
from .models import Customer, Scooter, Options, Booking, Manager
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from datetime import timedelta, datetime


# Login manager is used to perform tasks like logging users in and out
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)
login_manager.refresh_view = 'login'

# Prevents user session from being stolen
login_manager.session_protection = "strong"

# Session permanent is set to True, this forces user account to sign out after 2 hours.
# This only applies if the user did not tick the Remember Me checkbox
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60 * 2)

@login_manager.user_loader
def load_user(id):
    return Customer.query.get(int(id))


# Register view
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        user_exists = Customer.query.filter_by(email=email).first()
        if user_exists:
            flash('This email has already been used', category='error')
        else:
            password = form.password.data

            # Encrypts password using bcrypt, this is so the password is not shown as plain-text in the database.
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_customer = Customer(email=email, password=hashed_password)
            # Adds the customer account to the database
            db.session.add(new_customer)
            db.session.commit()
            flash('Successfully created account!', category='success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/registermanager', methods=['GET', 'POST'])
def register():
    form = RegisterManagerForm()

    if form.validate_on_submit():
        email = form.email.data
        user_exists = Manager.query.filter_by(email=email).first()
        if user_exists:
            flash('This email has already been used', category='error')
        elif form.managerPassword.data != "skrrtiscool123":
            flash('Manager password incorrect', category='error')
        else:
            password = form.password.data

            # Encrypts password using bcrypt, this is so the password is not shown as plain-text in the database.
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_manager = Manager(email=email, password=hashed_password)
            # Adds the customer account to the database
            db.session.add(new_manager)
            db.session.commit()
            flash('Successfully created account!', category='success')
            return redirect(url_for('login'))
    return render_template('ManagerRegister.html', title='Register', form=form)

# Login view
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Searches database for the inputted email name
        account = Customer.query.filter_by(email=form.email.data).first()
        # If the user has been found, then the following code is executed
        if account:
            # Checks to see if password from database matches the inputted password
            if bcrypt.check_password_hash(account.password, form.password.data):
                flash("Successfully logged in!", category='success')
                # If user has ticked remember me checkbox, then a remember me cookie is created locally
                if form.remember.data:
                    # Cookie will stay alive for 14 days, once expired the user will need to sign in again
                    # If user signs out manually or clears cookies from browser then the user will need to sign in again
                    login_user(account, remember=True, duration=timedelta(days=14))
                    return redirect(url_for('index'))
                else:
                    # No cookies used, instead a session with a set duration is used
                    login_user(account, remember=False)
                    return redirect(url_for('index'))
            else:
                # If the password is incorrect, error message is displayed
                flash('Email or password is incorrect', category='error')
        else:
            # If the email does not exist in the database, error message is displayed
            flash('This email does not exist', category='error')
    return render_template('login.html', title='Login', form=form, account=current_user)


# If user clicks log out, then user logs out and gets redirected to the login page
@app.route('/logout')
@login_required
def logout():
    flash('Successfully logged out!', category='success')
    logout_user()
    return redirect(url_for('login'))


# Home view
@app.route('/')
@app.route('/index')
@login_required
def index():
    home={'description':'Welcome.'}
    return render_template('home.html', title='Home', home=home, account=current_user)

@app.route('/addscooters', methods=['GET', 'POST'])
def addscooters():
    form = ScooterForm()
    if form.validate_on_submit():
        nlocation=request.form.get("location")
        new_scooter=Scooter(location = nlocation, availability = True)
        db.session.add(new_scooter)
        db.session.commit()
        flash("Scooter added")
        return redirect(url_for("addscooters"))

    return render_template('addscooters.html', title='Scooters', form=form)

@app.route('/addoptions', methods=['GET', 'POST'])
def addoptions():
    form = OptionsForm()
    if form.validate_on_submit():
        nhours=request.form.get("hours")
        nprice=request.form.get("price")
        new_option=Options(hours = nhours, price = nprice)
        db.session.add(new_option)
        db.session.commit()
        flash("Option added")
        return redirect(url_for("addoptions"))

    return render_template('addoptions.html', title='Options', form=form)

@app.route('/viewscooters', methods=['GET', 'POST'])
def viewscooters():
    scooters = Scooter.query.all()
    return render_template('viewscooters.html', title='Scooters', scooters=scooters)

@app.route('/book_scooter/<int:scooter_id>', methods=['GET', 'POST'])
def mark_task(scooter_id):
    options = Options.query.all()
    return render_template('options.html', title='Options', options=options, id = scooter_id)

@app.route('/book_scooter/<int:scooter_id>/<int:option_id>', methods=['GET', 'POST'])
def book_scooter(scooter_id, option_id):
    scooter = Scooter.query.get(scooter_id)
    scooter.availability = False
    bookingOption = Options.query.get(option_id)
    userId = current_user.get_id()
    newBooking = Booking(customerId = userId, scooterId = scooter.id, price = bookingOption.price, hours = bookingOption.hours)
    db.session.add(newBooking)
    db.session.commit()
    flash("Scooter booked")
    return redirect(url_for("payment"))

@app.route('/book_scooter/confirmation_page', methods=['GET', 'POST'])
def confirmation_page():
    customerId = current_user.get_id()
    booking = Booking.query.filter_by(customerId=customerId).order_by(Booking.bookingId.desc()).first()
    return render_template('bookingConfirmation.html', title='Confirmation', booking = booking)


@app.route('/payment', methods=['GET', 'POST'])#the way this should work is that you get routed here after making a booking
def payment():
    form = PaymentForm()
    if form.validate_on_submit():
        flash("Payment Succesful")
        return redirect(url_for("confirmation_page"))
    return render_template('payment.html', title='Payment', form=form)#instead of this, the available scooter should be updated
