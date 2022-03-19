from flask import render_template, flash, request, redirect, url_for, session
from app import app, db, bcrypt
from .forms import RegisterForm, LoginForm, ScooterForm, OptionsForm, PaymentForm, RegisterManagerForm, AddPaymentMethodForm, FeedbackForm
from .models import Account, Scooter, Options, Booking, PaymentCard, FeedbackCard
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from datetime import timedelta, datetime
import datetime as dt
from flask_mail import Mail, Message

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '95ebe879afef61'
app.config['MAIL_PASSWORD'] = '3ad9d8c3d9cfba'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

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
    return Account.query.get(int(id))


# Register view
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        user_exists = Account.query.filter_by(email=email).first()
        if user_exists:
            flash('This email has already been used', category='error')
        else:
            # A customer account is indicated by its role number which is 1.
            # This will be used to restrict customer from accessing manager views
            role = 1
            password = form.password.data
            student = form.student.data
            seniorCitizen = form.seniorCitizen.data
            if student == True and seniorCitizen == True:
                flash('Cant apply for student discount and senior citizen discount', category='error')
                return redirect(url_for('register'))
            # Encrypts password using bcrypt, this is so the password is not shown as plain-text in the database.
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_customer = Account(email=email, password=hashed_password, role=role,student=student,seniorCitizen=seniorCitizen)
            # Adds the customer account to the database
            db.session.add(new_customer)
            db.session.commit()
            flash('Successfully created account!', category='success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/registermanager', methods=['GET', 'POST'])
def registermanager():
    form = RegisterManagerForm()

    if form.validate_on_submit():
        email = form.email.data
        user_exists = Account.query.filter_by(email=email).first()
        if user_exists:
            flash('This email has already been used', category='error')
        elif form.managerPassword.data != "asdfghjk":
            flash('Manager password incorrect', category='error')
        else:
            # A manager account is indicated by its role number which is 2.
            # This will be used to restrict manager from accessing customer views
            role = 2
            password = form.password.data

            # Encrypts password using bcrypt, this is so the password is not shown as plain-text in the database.
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_manager = Account(email=email, password=hashed_password, role=role,student=False,seniorCitizen=False)
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
        account = Account.query.filter_by(email=form.email.data).first()
        # If the user has been found, then the following code is executed
        if account and account.role == 1:
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
        elif account and account.role == 2:
            # Checks to see if password from database matches the inputted password
            if bcrypt.check_password_hash(account.password, form.password.data):
                flash("Successfully logged in!", category='success')
                # If user has ticked remember me checkbox, then a remember me cookie is created locally
                if form.remember.data:
                    # Cookie will stay alive for 14 days, once expired the user will need to sign in again
                    # If user signs out manually or clears cookies from browser then the user will need to sign in again
                    login_user(account, remember=True, duration=timedelta(days=14))
                    return redirect(url_for('managerindex'))
                else:
                    # No cookies used, instead a session with a set duration is used
                    login_user(account, remember=False)
                    return redirect(url_for('managerindex'))
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
def index():
    home={'description':'Welcome.'}
    return render_template('home.html', title='Home', home=home, account=current_user)

@app.route('/managerindex')
@login_required
def managerindex():
    if current_user.role == 2:
        home={'description':'Welcome.'}
        return render_template('managerHome.html', title='Home', home=home, account=current_user)
    else:
        flash('You are not authorised to view this page', category='error')
        return redirect(url_for('index'))





@app.route('/addscooters', methods=['GET', 'POST'])
def addscooters():
    if current_user.role == 2:
        form = ScooterForm()
        if form.validate_on_submit():
            nlocation=request.form.get("location")
            new_scooter=Scooter(location = nlocation, availability = True)
            db.session.add(new_scooter)
            db.session.commit()
            flash("Scooter added")
            return redirect(url_for("addscooters"))
        return render_template('addscooters.html', title='Scooters', form=form)
    else:
        flash('You are not authorised to view this page', category='error')
        return redirect(url_for('index'))


@app.route('/addoptions', methods=['GET', 'POST'])
def addoptions():
    if current_user.role == 2:
        form = OptionsForm()
        if form.validate_on_submit():
            nhours = request.form.get("hours")
            nprice = request.form.get("price")
            new_option = Options(hours=nhours, price=nprice)
            db.session.add(new_option)
            db.session.commit()
            flash("Option added")
            return redirect(url_for("addoptions"))
        return render_template('addoptions.html', title='Options', form=form)
    else:
        flash('You are not authorised to view this page', category='error')
        return redirect(url_for('index'))

@app.route('/viewscooters', methods=['GET', 'POST'])
def viewscooters():
    scooters = Scooter.query.all()
    return render_template('viewscooters.html', title='Scooters', scooters=scooters)



@app.route('/book_scooter/<int:scooter_id>', methods=['GET', 'POST'])
def mark_task(scooter_id):
    if current_user.role == 1:
        options = Options.query.all()
        return render_template('options.html', title='Options', options=options, id=scooter_id)
    else:
        flash('Our services are available to our customers only', category='error')
        return redirect(url_for('managerindex'))

@app.route('/book_scooter/<int:scooter_id>/<int:option_id>', methods=['GET', 'POST'])
def book_scooter(scooter_id, option_id):
    if current_user.role == 1:
        #get current date
        cDate = dt.date.today()
        strDate = cDate.strftime("%D")#convert into string

        scooter = Scooter.query.get(scooter_id)
        scooter.availability = False
        bookingOption = Options.query.get(option_id)
        userId = current_user.get_id()
        newBooking = Booking(customerId = userId, scooterId = scooter.id, price = bookingOption.price, hours = bookingOption.hours, date=strDate)
        db.session.add(newBooking)
        db.session.commit()
        flash("Scooter booked")
        return redirect(url_for("payment"))
    else:
        flash('Our services are available to our customers only', category='error')
        return redirect(url_for('managerindex'))

@app.route('/book_scooter/confirmation_page', methods=['GET', 'POST'])
def confirmation_page():
    if current_user.role == 1:
        customerId = current_user.get_id()
        booking = Booking.query.filter_by(customerId=customerId).order_by(Booking.bookingId.desc()).first()
        nemail = Account.query.get(customerId)
        msg = Message('Booking Confirmation', sender =   'raja@mailtrap.io', recipients = [nemail.email])
        msg.body = 'Hello ' + str(nemail.email) + '\nBooking ID: '  + str(booking.bookingId) + '\nCustomer ID: ' + str(booking.customerId) + '\nScooter ID: ' + str(booking.scooterId) + '\nPrice: ' + str(booking.price) + '\nHourse: ' + str(booking.hours)
        mail.send(msg)
        return render_template('bookingConfirmation.html', title='Confirmation', booking = booking)
    else:
        flash('Our services are available to our customers only', category='error')
        return redirect(url_for('managerindex'))

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if current_user.role == 1:
        form = PaymentForm()
        if form.validate_on_submit():
            flash("Payment Succesful")
            return redirect(url_for("confirmation_page"))
        return render_template('payment.html', title='Payment', form=form)
    else:
        flash('Our services are available to our customers only', category='error')
        return redirect(url_for('managerindex'))

@app.route('/add_payment_details', methods=['GET','POST'])
def add_payment_details():
    if current_user.role == 1:
        form = AddPaymentMethodForm()
        if form.validate_on_submit():
            ncardNumber = request.form.get("cardNum")
            nexpiryDate = request.form.get("expiryDate")
            ncardName = request.form.get("cardName")
            new_card = PaymentCard(digit16=ncardNumber, ExpiryDate=nexpiryDate, CardName=ncardName,
                                   CustomerId=current_user.get_id())
            db.session.add(new_card)
            db.session.commit()
            flash("Payment Method Added")
            return redirect(url_for("index"))
        return render_template('addPayment.html', title='Add Payment Detail', form=form)
    else:
        flash('Our services are available to our customers only', category='error')
        return redirect(url_for('managerindex'))

@app.route('/send_feedback_form', methods=['GET','POST'])
def feedback_form():
    if current_user.role == 1:
        form = FeedbackForm()
        if form.validate_on_submit():
            nScooterId = request.form.get("scooterId")
            nfeedback = request.form.get("feedback")
            new_feedback_form = FeedbackCard(scooterId=nScooterId, feedback=nfeedback)
            db.session.add(new_feedback_form)
            db.session.commit()
            flash("Feedback Form Sent")
            return redirect(url_for("index"))
        return render_template('FeedbackForm.html', title='Send Scooter Feedback', form=form)
    else:
        flash('Our services are available to our customers only', category='error')
        return redirect(url_for('managerindex'))

@app.route('/revenue', methods=['GET', 'POST'])
def revenue_page():

    #variable prep
    bookingFirst = Booking.query.order_by(Booking.bookingId.desc()).first()
    inBooking = bookingFirst.bookingId

    cDate = dt.date.today()#current date
    strDate = cDate.strftime("%D")#convert into string
    temp = strDate.split("/")#split the date into a list of month, date, year
    int1 = int(temp[1])

    foundDate = False
    count = 0
    totalPrice = 0

    while not foundDate:
        if inBooking - count > 0:
            tempBooking = Booking.query.filter_by(bookingId = inBooking - count).first()
            temp2 = tempBooking.date#format date until we only have an int of the days
            strTemp = temp2.split("/")
            int2 = int(strTemp[1])
            if (int1 - int2 > 7):#longer than a week ago we dont care about it anymore
                foundDate = True
            else:
                totalPrice += tempBooking.price
        else:
            foundDate = True
        count += 1

    return render_template('revenue.html', title='revenue', totalPrice = totalPrice)
