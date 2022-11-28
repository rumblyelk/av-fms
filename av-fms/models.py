from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, create_engine
from datetime import datetime

db = SQLAlchemy()

# TODO: look into adding class methods to the models such as to_dict() or filters such as filter_by_manufacturer(), which would make
# things a lot cleaner. For example, a query could be simple as "VehicleTask.filter_by_manufacturer('Tesla').from_with_last(1, 'week')"


class User(db.Model):
    id = db.Column(
        db.Integer, primary_key=True
    )
    username = db.Column(
        db.String(80), unique=True, nullable=False
    )
    password = db.Column(
        db.String(80), unique=True, nullable=False
    )
    role = db.Column(
        db.String(80), unique=False, nullable=False, default='USER'
    )
    tasks = db.relationship(
        'VehicleTask', backref='user', lazy=True
    )


class Vehicle(db.Model):
    id = db.Column(
        db.Integer, primary_key=True
    )
    manufacturer = db.Column(
        db.String(80), unique=False, nullable=False
    )
    license_plate_number = db.Column(
        db.String(80), unique=True, nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=True
    )
    available = db.Column(
        db.Boolean, unique=False, nullable=False, default=True
    )
    user = db.relationship(
        'User', backref='vehicle', lazy=True
    )
    tasks = db.relationship(
        'VehicleTask', backref='vehicle', lazy=True, cascade="all, delete-orphan"
    )


class VehicleTask(db.Model):
    id = db.Column(
        db.Integer, primary_key=True
    )
    vehicle_id = db.Column(
        db.Integer, db.ForeignKey('vehicle.id', ondelete='cascade'), nullable=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False
    )
    completed = db.Column(
        db.Boolean, unique=False, nullable=False, default=False
    )
    start_time = db.Column(
        db.DateTime, nullable=False, default=datetime.now()
    )
    end_time = db.Column(
        db.DateTime, nullable=True
    )
