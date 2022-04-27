from app import db
from flask_login import UserMixin


# Account model which stores both the customer and manager accounts
class Account(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    role = db.Column(db.Integer, primary_key=False)
    student = db.Column(db.Boolean)
    seniorCitizen = db.Column(db.Boolean)

class Scooter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String)
    availability = db.Column(db.Boolean, default = True)
    timeLeft = db.Column(db.Integer)

class Options(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hours = db.Column(db.Integer)
    price = db.Column(db.Integer)

class Booking(db.Model):
    bookingId = db.Column(db.Integer, primary_key=True)
    customerId = db.Column(db.Integer)
    scooterId = db.Column(db.Integer)
    price = db.Column(db.Integer)
    hours = db.Column(db.Integer)
    date = db.Column(db.String)
    datetime = db.Column(db.DateTime)

class PaymentCard(db.Model):
    digit16 = db.Column(db.Integer, primary_key=True)
    CustomerId = db.Column(db.Integer)
    ExpiryDate = db.Column(db.Integer)
    CardName = db.Column(db.String)

class FeedbackCard(db.Model):
    feedbackId=db.Column(db.Integer, primary_key=True)
    scooterId =db.Column(db.Integer)
    feedback=db.Column(db.String)
    feedbackPriority=db.Column(db.Integer)

class UnregisteredBooking(db.Model):
    bookingId = db.Column(db.Integer, primary_key=True)
    scooterId = db.Column(db.Integer)
    email = db.Column(db.String)
    price = db.Column(db.Integer)
    hours = db.Column(db.Integer)
    date = db.Column(db.String)
