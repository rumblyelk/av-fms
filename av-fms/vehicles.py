import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .models import db, Vehicle, User

bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')


@bp.route('/')
def index():
    vehicles = Vehicle.query.all()
    users = {
        user.id: user for user in
        User.query.filter(User.id.in_(
            [vehicle.user_id for vehicle in vehicles if vehicle.user_id]
        ))
        .all()
    }
    create_staff_user()
    return render_template('vehicles/index.html', vehicles=vehicles, users=users)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        man = request.form['manufacturer']
        lpn = request.form['license_plate_number']

        error = None
        if not man:
            error = 'Manufacturer is required.'
        elif not lpn:
            error = 'License plate number is required.'

        if error is None:
            try:
                new_vehicle = Vehicle(man, lpn)
                db.session.add(new_vehicle)
                db.session.commit()
            except Exception:
                error = f'Vehicle "{lpn}" is already registered.'
            else:
                return redirect(url_for('vehicles.index'))

        if error is not None:
            flash(error)
        else:
            flash('Vehicle successfully created.')

    return render_template('vehicles/create.html')


@bp.route('/take_vehicle', methods=('GET', 'POST'))
def take_vehicle():
    vid = request.args.get('vid')
    vehicle = Vehicle.query.filter_by(id=vid).first()
    vehicle.user_id = g.user.id
    vehicle.available = False
    db.session.commit()

    return redirect(url_for('vehicles.index'))


@bp.route('/return_vehicle', methods=('GET', 'POST'))
def return_vehicle():
    vid = request.args.get('vid')
    vehicle = Vehicle.query.filter_by(id=vid).first()
    vehicle.user_id = None
    vehicle.available = True
    db.session.commit()

    return redirect(url_for('vehicles.index'))


def create_staff_user():
    """
    Since this whole system is a demo, this code is here to provide a staff user for testing.
    After creating a normal user for the first time and loading the vehicles page, the ability
    to log in with a staff role with the following credentials will be available:
        username: staffUser
        password: staffpass
    """
    staff_user = User.query.filter_by(username='staffUser').first()

    if staff_user is None:
        staff_user = User(username='staffUser', password=generate_password_hash(
            'staffpass'), role='STAFF')
        db.session.add(staff_user)
        db.session.commit()
