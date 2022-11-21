from flask_sqlalchemy import SQLAlchemy

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
