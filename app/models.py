from app import db
from flask_login import UserMixin


# Customer account model
class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)

class Manager(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)

class Scooter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String)
    availability = db.Column(db.Boolean, default = True)

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

class PaymentCard(db.Model):
    digit16 = db.Column(db.Integer, primary_key=True)
    CustomerId = db.Column(db.Integer)
    ExpiryDate = db.Column(db.Integer)
    CardName = db.Column(db.String)

class FeedbackCard(db.Model):
    feedbackId=db.Column(db.Integer, primary_key=True)
    scooterId =db.Column(db.Integer)
    feedback=db.Column(db.String)
