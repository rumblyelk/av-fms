from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(80), unique=False, nullable=False)

    def __init__(self, username, password, role='USER'):
        self.username = username
        self.password = password
        self.role = role


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(80), unique=False, nullable=False)
    license_plate_number = db.Column(
        db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    available = db.Column(db.Boolean, unique=False,
                          nullable=False, default=True)

    def __init__(self, manufacturer, license_plate_number, user_id=None, available=True):
        self.manufacturer = manufacturer
        self.license_plate_number = license_plate_number
        self.user_id = user_id
        self.available = available


class VehicleTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, unique=False,
                          nullable=False, default=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)

    def __init__(self, vehicle_id, user_id, start_time=datetime.datetime.now(), end_time=None):
        self.vehicle_id = vehicle_id
        self.user_id = user_id
        self.start_time = start_time
        self.end_time = end_time
