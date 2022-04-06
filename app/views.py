from flask import render_template, flash, request, redirect, url_for, session
from app import app, db, bcrypt
from .forms import RegisterForm, LoginForm, ScooterForm, OptionsForm, PaymentForm, RegisterManagerForm, AddPaymentMethodForm, FeedbackForm, UnregisteredPaymentForm
from .models import Account, Scooter, Options, Booking, PaymentCard, FeedbackCard, UnregisteredBooking
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from datetime import timedelta, datetime
import datetime as dt
from flask_mail import Mail, Message
import math


# Sends mail through the SMTP protocol
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
                flash('Cant apply for student discount and senior citizen discount',
                    category='error')
                return redirect(url_for('register'))
            # Encrypts password using bcrypt, this is so the password is not shown as
            # plain-text in the database.
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_customer = Account(email=email, password=hashed_password, role=role,
                student=student,seniorCitizen=seniorCitizen)
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

            # Encrypts password using bcrypt, this is so the password is not shown as plain-text
            # in the database.
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_manager = Account(email=email, password=hashed_password, role=role,student=False,
                seniorCitizen=False)
            # Adds the customer account to the database
            db.session.add(new_manager)
            db.session.commit()
            flash('Successfully created account!', category='success')
            return redirect(url_for('login'))
    return render_template('ManagerRegister.html', title='Register', form=form)


# Login view
@app.route('/', methods=['GET', 'POST'])
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
                # If user has ticked remember me checkbox, then a remember me cookie is
                # created locally
                if form.remember.data:
                    # Cookie will stay alive for 14 days, once expired the user will need to sign
                    # in again. If user signs out manually or clears cookies from browser then the
                    # user will need to sign in again
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
                # If user has ticked remember me checkbox, then a remember me cookie is
                # created locally
                if form.remember.data:
                    # Cookie will stay alive for 14 days, once expired the user will need to
                    # sign in again. If user signs out manually or clears cookies from browser then
                    # the user will need to sign in again
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
@app.route('/index')
def index():
    home={'description':'Welcome.'}
    return render_template('home.html', title='Home', home=home, account=current_user)


# Manager home view
@app.route('/managerindex')
@login_required
def managerindex():
    if current_user.role == 2:
        home={'description':'Welcome.'}
        return render_template('managerHome.html', title='Home', home=home, account=current_user)
    else:
        flash('You are not authorised to view this page', category='error')
        return redirect(url_for('index'))


# Add scooters view
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


# Add options view
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


# View scooters
@app.route('/viewscooters', methods=['GET', 'POST'])
def viewscooters():
    booking = Booking.query.all()
    nscooters = Scooter.query.order_by(Scooter.id.desc()).first()
    cDateTime = dt.datetime.now()
    if nscooters is not None:
        numScooters = nscooters.id
        for i in range(1, numScooters):
            bookingFirst = Booking.query.filter_by(scooterId= i).order_by(Booking.bookingId.desc()).first()
            if bookingFirst is None:
                continue
            if (((cDateTime - bookingFirst.datetime).total_seconds())/3600) > bookingFirst.hours:
                 scooter = Scooter.query.filter_by(id = i).first()
                 if scooter is not None:
                     scooter.availability = True
                     db.session.commit()
    scooters = Scooter.query.all()
    return render_template('viewscooters.html', title='Scooters', scooters=scooters)



# Manager can view feedback
@app.route('/view_feedback', methods=['GET', 'POST'])
def view_feedback():
    if current_user.role == 2:
        feedbackCards = FeedbackCard.query.order_by(FeedbackCard.feedbackPriority.desc()).all()
        return render_template('viewfeedback.html', title='Feedback', feedbackCards=feedbackCards)
    else:
        flash('This page is accessed by managers only', category='error')
        return redirect(url_for('index'))


@app.route('/view_feedback/resolve_feedback/<int:feedbackId>', methods=['GET', 'POST'])
def resolve_feedback(feedbackId):
    FeedbackCard.query.filter_by(feedbackId = feedbackId).delete()
    db.session.commit()
    flash('Issue removed from database!', category='success')
    return redirect(url_for('view_feedback'))

@app.route('/remove_scooters', methods=['GET', 'POST'])
def remove_scooters():
    if current_user.role == 2:
        unusedScooters = Scooter.query.filter_by(availability = True).all()
        return render_template('removeScooters.html', title='Unused Scooters', unusedScooters = unusedScooters)
    else:
        flash('This page is accessed by managers only', category='error')
        return redirect(url_for('index'))

@app.route('/remove_scooters/delete_scooter/<int:id>', methods=['GET', 'POST'])
def delete_scooter(id):
    Scooter.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Scooter removed from database!', category='success')
    return redirect(url_for('remove_scooters'))


# Book scooters view
@app.route('/book_scooter/<int:scooter_id>', methods=['GET', 'POST'])
def choose_option(scooter_id):
    if current_user.role == 1:
        options = Options.query.all()
        weeklyScooterTime = weekly_usage_calculator()
        # Should the discount be applied?
        if current_user.student == True or current_user.seniorCitizen == True or weeklyScooterTime > 7:
            flash('Discount applied!',category='success')
            for option in options:
                option.price = math.ceil(option.price * 0.8)

        userId = current_user.get_id()
        paymentCard = PaymentCard.query.filter_by(CustomerId = userId).first()
        if (paymentCard is not None):
            paymentId = paymentCard.CustomerId
        else:
            paymentId = 0
        return render_template('options.html', title='Options', options=options, id=scooter_id,
            paymentId=paymentId)
    else:
        flash('Our services are available to our customers only', category='error')
        return redirect(url_for('managerindex'))

def weekly_usage_calculator():
    hourCounter = 0
    # Get all bookings
    bookings = Booking.query.all()
    # Get todays date
    today = dt.date.today()
    for booking in bookings:
        # Create a date object from string in database
        bookingDateObject = dt.datetime.strptime(booking.date, "%m/%d/%y").date()
        # Floor division to calculate difference in weeks
        weekDifference = (today-bookingDateObject).days//7
        # If this user has a booking in the most recent week then add to counter
        if booking.customerId == current_user.id and weekDifference == 0:
            hourCounter = hourCounter + booking.hours
    return hourCounter


@app.route('/book_scooter/<int:scooter_id>/<int:option_id>/<int:paymentId>', methods=['GET', 'POST'])
def storedpaymentbook(scooter_id, option_id, paymentId):
    if current_user.role == 1:
        # Get current date
        cDate = dt.date.today()
        strDate = cDate.strftime("%D")  # convert into string

        scooter = Scooter.query.get(scooter_id)
        scooter.availability = False
        bookingOption = Options.query.get(option_id)

        # Apply discount for student and senior citizen
        weeklyScooterTime = weekly_usage_calculator()
        if current_user.student == True or current_user.seniorCitizen == True or weeklyScooterTime > 7:
            bookingOption.price = math.ceil(bookingOption.price * 0.8)

        userId = current_user.get_id()
        cDateTime = dt.datetime.now()
        newBooking = Booking(customerId = userId, scooterId = scooter.id, price = bookingOption.price,
            hours = bookingOption.hours, date=strDate, datetime = cDateTime)
        db.session.add(newBooking)
        db.session.commit()
        flash("Scooter booked")
        return redirect(url_for("confirmation_page"))
    else:
        flash('Our services are available to our customers only', category='error')
        return redirect(url_for('managerindex'))


@app.route('/book_scooter/<int:scooter_id>/<int:option_id>', methods=['GET', 'POST'])
def book_scooter(scooter_id, option_id):
    if current_user.role == 1:
        # Get current date
        cDate = dt.date.today()
        strDate = cDate.strftime("%D")  # convert into string

        scooter = Scooter.query.get(scooter_id)
        scooter.availability = False
        bookingOption = Options.query.get(option_id)

        #apply discount for student and senior citizen
        weeklyScooterTime = weekly_usage_calculator()
        if current_user.student == True or current_user.seniorCitizen == True or weeklyScooterTime > 7:
            bookingOption.price = math.ceil(bookingOption.price * 0.8)

        userId = current_user.get_id()
        cDateTime = dt.datetime.now()
        newBooking = Booking(customerId = userId, scooterId = scooter.id, price = bookingOption.price,
            hours = bookingOption.hours, date=strDate, datetime = cDateTime)
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


# Payment view
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


# Add payment details view
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


# Send feedback view
@app.route('/send_feedback_form', methods=['GET','POST'])
def feedback_form():
    if current_user.role == 1:
        form = FeedbackForm()
        if form.validate_on_submit():
            nScooterId = request.form.get("scooterId")
            nfeedback = request.form.get("feedback")
            nPriority = request.form.get("feedbackPriority")
            new_feedback_form = FeedbackCard(scooterId=nScooterId, feedback=nfeedback, feedbackPriority=nPriority)
            db.session.add(new_feedback_form)
            db.session.commit()
            flash("Feedback Form Sent")
            return redirect(url_for("index"))
        return render_template('FeedbackForm.html', title='Send Scooter Feedback', form=form)
    else:
        flash('Our services are available to our customers only', category='error')
        return redirect(url_for('managerindex'))


@app.route('/unregistered_booking', methods=['GET', 'POST'])
def unregistered_booking():
        scooters = Scooter.query.all()
        return render_template('unregisteredBooking.html', title='Scooters', scooters=scooters)


@app.route('/unregistered_book_scooter/<int:scooter_id>', methods=['GET', 'POST'])
def unregistered_view_options(scooter_id):
        options = Options.query.all()
        return render_template('unregisteredOptions.html', title='Options', options=options, id=scooter_id)


@app.route('/unregistered_book_scooter/<int:scooter_id>/<int:option_id>', methods=['GET', 'POST'])
def unregistered_book_scooter(scooter_id, option_id):
        #get current date
        cDate = dt.date.today()
        strDate = cDate.strftime("%D")  # convert into string
        scooter = Scooter.query.get(scooter_id)
        scooter.availability = False
        bookingOption = Options.query.get(option_id)
        newBooking = UnregisteredBooking(scooterId = scooter.id, price = bookingOption.price, hours = bookingOption.hours, date=strDate)
        db.session.add(newBooking)
        db.session.commit()
        flash("Scooter booked")
        return redirect(url_for("unregistered_payment"))


@app.route('/unregistered_book_scooter/unregistered_confirmation_page', methods=['GET', 'POST'])
def unregistered_confirmation_page():
        booking = UnregisteredBooking.query.order_by(UnregisteredBooking.bookingId.desc()).first()
        nemail = booking.email
        msg = Message('Booking Confirmation', sender =   'raja@mailtrap.io', recipients = [nemail])
        msg.body = 'Hello ' + str(nemail) + '\nBooking ID: '  + str(booking.bookingId) + '\nScooter ID: ' + str(booking.scooterId) + '\nPrice: ' + str(booking.price) + '\nHours: ' + str(booking.hours)
        mail.send(msg)
        return render_template('unregisteredConfirmation.html', title='Confirmation', booking = booking)


@app.route('/unregisteredpayment', methods=['GET', 'POST'])
def unregistered_payment():
        form = UnregisteredPaymentForm()
        if form.validate_on_submit():
            flash("Payment Succesful")
            booking = UnregisteredBooking.query.order_by(UnregisteredBooking.bookingId.desc()).first()
            booking.email = form.email.data
            db.session.commit()
            return redirect(url_for("unregistered_confirmation_page"))
        return render_template('unregisteredPayment.html', title='Payment', form=form)


# View bookings view
@app.route('/viewbookings', methods=['GET', 'POST'])
def viewbookings():
    if current_user.role == 1:
        customerId = current_user.get_id()
        bookings = Booking.query.filter_by(customerId=customerId)
        cDateTime = dt.datetime.now()
        ongoing = list()
        expired = list()
        for booking in bookings:
            if (((cDateTime - booking.datetime).total_seconds())/3600) > booking.hours:
                expired.append(booking)
            else:
                ongoing.append(booking)
    return render_template('viewBookings.html', title='Bookings', ongoing=ongoing, expired = expired)


@app.route('/cancel_booking/<int:bookingId>', methods=['GET', 'POST'])
def cancel_booking(bookingId):
    booking = Booking.query.filter_by(bookingId=bookingId).first()
    booking.hours = 0;
    db.session.commit()
    return redirect(url_for('viewbookings'))


@app.route('/extend_booking/<int:bookingId>', methods=['GET', 'POST'])
def extend_booking(bookingId):
    options = Options.query.all()
    return render_template('extendingOptions.html', title='Options', options=options, bookingId=bookingId)


@app.route('/extend_scooter_option/<int:bookingId>/<int:option_id>', methods=['GET', 'POST'])
def extend_booking_option(bookingId, option_id):
    booking = Booking.query.filter_by(bookingId=bookingId).first()
    bookingOption = Options.query.get(option_id)
    booking.hours = booking.hours + bookingOption.hours
    booking.price = booking.price + bookingOption.price
    db.session.commit()
    return redirect(url_for('viewbookings'))


@app.route('/revenue', methods=['GET', 'POST'])
def revenue_page():
    # Restrict customers from viewing revenue
    if (current_user.role == 2) == False:
        flash('You are not authorised to view this page', category='error')
        return redirect(url_for('index'))

    weekPrice = 0
    weekPrices =[]
    weekDates = []
    percentages = []
    labels = []
    values = []
    dayPrice = 0
    weekPriceLen = 0
    popularDay = 6    # in case our db is empty
    percentagesLen = 0
    month = todaysMonth(todaysDate())   # the current month
    today = todaysDay(todaysDate()) # the current day
    testBooking = Booking.query.order_by(Booking.bookingId.desc()).first()  # this will only wbe used to check if the database is empty


    if (testBooking != None):   # our database is not empty
        dayPrice = calculateRevenue(1)
        weekPrice = calculateRevenue(7)
        for i in range(6, -1, -1):  # Note: calculateDailyRevenue() works with a different index than its counterpart
            # while calculateRevenue goes from 1...7 this one goes from 6...0 for a week
            weekPrices.append(calculateDailyRevenue(i))
            weekDates.append(today-i)   # the number dates corresponding to each revenue
        weekPriceLen = len(weekPrices)
        popularDay = weekDates[calculatePopularDay(weekPrices)] # the index is shared so if most revenue is at index 3 so will be the date
        percentages = findOptionPercentage(popularDay)  # a list of the percentages for each booking, 2 d
        percentagesLen = len(percentages)
        # Our final two variables, which will be used in the graphs
        labels = [row[0] for row in percentages]    # the number of hours rented, on the most popular day
        values = [row[1] for row in percentages]    # the percentage of people who rented each hour
    else:   # our database is empty so return 0

        weekPrice = 0
        dayPrice = 0

    return render_template('revenue.html', title='revenue', weekPrice = weekPrice,
    dayPrice = dayPrice, weekPrices = weekPrices, month = month, weekPriceLen = weekPriceLen,

    weekDates = weekDates, popularDay = popularDay, percentages = percentages, percentagesLen = percentagesLen,
    labels = labels, values = values)


# These are our functional methods
def calculateRevenue(days): # a revenue calculating method based around the number of days you want the revenue for
    # Returns the total price in the date range
    # ex, for todays date, number of days would be 1

    bookingFirst = Booking.query.order_by(Booking.bookingId.desc()).first()
    inBooking = bookingFirst.bookingId
    foundDate = False
    count = 0
    totalPrice = 0
    temp = todaysDate()
    thisMonth = int(temp[0])    # the month it is currently
    today = int(temp[1])    # the day it is today

    while not foundDate:    # loop through the database until we find a date which is longer ago than what we want, a week
        if inBooking - count > 0:   # we have reached the end of the database
            tempBooking = Booking.query.filter_by(bookingId = inBooking - count).first()#the latest booking
            temp2 = tempBooking.date    # format date until we only have an int of the days
            strTemp = temp2.split("/")  # some formatting
            searchDate = int(strTemp[1])
            searchMonth = int(strTemp[0])
            if (today - searchDate >= days or (thisMonth - searchMonth != 0)):  # longer than a week ago we dont care about it anymore
                foundDate = True    # alternatively, if it is a different month, we also don't care
            else:
                totalPrice += tempBooking.price
        else:
            foundDate = True
        count += 1
    return totalPrice


def calculateDailyRevenue(days):    # this method calculates the revenue of a specific day
    # input: how many days back is the specific day
    # like calculateRevenue() but not quite
    bookingFirst = Booking.query.order_by(Booking.bookingId.desc()).first()
    inBooking = bookingFirst.bookingId
    foundDate = False
    count = 0
    totalPrice = 0
    temp = todaysDate()
    thisMonth = int(temp[0])    # the month it is currently
    today = int(temp[1])    # the day it is today

    while not foundDate:    # loop through the database until we find a date which is longer ago than what we want, a week
        if inBooking - count > 0:   # we have reached the end of the database
            tempBooking = Booking.query.filter_by(bookingId = inBooking - count).first()    # the latest booking
            temp2 = tempBooking.date    # format date until we only have an int of the days
            strTemp = temp2.split("/")  # some formatting
            searchDate = int(strTemp[1])
            searchMonth = int(strTemp[0])
            if (today - searchDate == days):    # if it is the targeted date
                totalPrice += tempBooking.price

            if (today - searchDate > days or (thisMonth - searchMonth != 0)):   # longer than a week ago we dont care about it anymore
                foundDate = True    # alternatively, if it is a different month, we also don't care
        else:
            foundDate = True
        count += 1
    return totalPrice


def calculatePopularDay(prices):
    largest = 0
    index = 6    # the only way this wouldnt change is if theyre all 0, so the biggest may as well be 0
    for i in range(len(prices)):
        if prices[i] > largest:
            index = i
            largest = prices[i]
    return index


def findOptionPercentage(targetDate):   # returns the percentage of each option chosen for a specific day
    # input: the number of a specific day
    # like calculateDailyRevenue() but not quite
    temp = todaysDate()
    thisMonth = int(temp[0])#the month it is currently
    bookingFirst = Booking.query.order_by(Booking.bookingId.desc()).first()
    inBooking = bookingFirst.bookingId
    foundDate = False
    count = 0
    optionsRented = []  # this will be a list full of each hour rented for every date that matches
    percentages = []
    while not foundDate:    # loop through the database until we find a date which is longer ago than what we want, a week
        if inBooking - count > 0:   # we have reached the end of the database
            tempBooking = Booking.query.filter_by(bookingId = inBooking - count).first()    # the latest booking
            temp2 = tempBooking.date    # format date until we only have an int of the days
            strTemp = temp2.split("/")  # some formatting
            searchDate = int(strTemp[1])
            searchMonth = int(strTemp[0])
            if (searchDate == targetDate):  # if it is the targeted date
                optionsRented.append(tempBooking.hours)

            if ((thisMonth - searchMonth != 0) or targetDate > searchDate):
                foundDate = True    # if it is a different month, we also don't care
        else:
            foundDate = True
        count += 1
    percentages = makePercentages(optionsRented)
    return percentages


def makePercentages(inList):    # input is a list of different rental options
    # the method counts duplicates and makes a list of each number of requested options
    optionsCount = []   # these lists will share their index
    options = []
    total = 0

    for i in range(0, len(inList)):
        if inList[i] not in options and inList[i] != 0: # a new unique option
            options.append(inList[i])   # add it to the list of options
            optionsCount.append(1)  # our count starts at 1
        else:
            for j in range(0, len(optionsCount)):   # look for the option in the array
                if (optionsCount[j] == inList[i]):
                    break   # we found it so stop the loop
                optionsCount[j] = optionsCount[j] + 1

    # Now we make a 2d array, with the left side being the number of hours and the right side the percentage
    percentageAndOptions = []
    rows = len(options) # we will have as many wors as we have unique options
    cols = 2    # left is option, right is percentage
    percentageAndOptions = [[0 for i in range(cols)] for j in range(rows)]

    # Now we make a 2d array, with the left side being the number of hours and the right side the percentage
    percentageAndOptions = []
    rows = len(options) # we will have as many wors as we have unique options
    cols = 2    # left is option, right is percentage
    percentageAndOptions = [[0 for i in range(cols)] for j in range(rows)]

    for i in range(0, len(optionsCount)):
        total += optionsCount[i]    # get the total number of rentals

    for i in range(0, len(optionsCount)):
        percentage = (optionsCount[i]/total) * 100  # calculate the percentage
        roundedPercentage = round(percentage, 2)
        percentageAndOptions[i][0] = options[i]
        percentageAndOptions[i][1] = roundedPercentage

    return percentageAndOptions

def todaysMonth(temp):  # input: a split list of the date it is today (see todaysDate())
    # Output: corresponding month as a string
    # list of months
    months = [ "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    thisMonth = int(temp[0])
    month = months[thisMonth-1] # the month it is today as a word
    return month

def todaysDate():   # outputs a split list of month, day, year, in that order
    cDate = dt.date.today() # current date
    strDate = cDate.strftime("%D")  # convert into string
    dates = strDate.split("/")  # split the date into a list of month, date, year
    return dates

def todaysDay(tempString):  # returns the day it is today as an int
    # input same as todaysMonth
    today = int(tempString[1])
    return today
