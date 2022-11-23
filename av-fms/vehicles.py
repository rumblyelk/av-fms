import datetime
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .models import db, Vehicle, User, VehicleTask

bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')


@bp.route('/')
def index():
    vehicles = Vehicle.query.all()
    users = {
        user.id: user for user in
        User.query.filter(User.id.in_(
            [vehicle.user_id for vehicle in vehicles if vehicle.user_id]
        )).all()
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

        if error:
            flash(error)
        else:
            flash('Vehicle successfully created.')

    return render_template('vehicles/create.html')


@bp.route('/delete', methods=('GET', 'POST'))
def delete():
    """
    An optional additional action that may need to be added would be to delete the Tasks associated with a Vehicle as well.
    """
    error = None
    if g.user.role != 'STAFF':
        error = "You are not authorized to perform this action."

    vid = request.args.get('vid')
    vehicle = Vehicle.query.filter_by(id=vid).first()

    if error is None:
        try:
            db.session.delete(vehicle)
            db.session.commit()
        except Exception:
            error = "Vehicle could not be deleted."
        else:
            return redirect(url_for('vehicles.index'))

    if error:
        flash(error)

    return render_template('vehicles/index.html')


@bp.route('/take_vehicle', methods=('GET', 'POST'))
def take_vehicle():
    error = None
    user_vehicle = Vehicle.query.filter_by(
        user_id=g.user.id).first()
    if user_vehicle:
        error = f'You already have taken the {user_vehicle.manufacturer} | {user_vehicle.license_plate_number}.'

    if error is None:
        vid = request.args.get('vid')

        vehicle = Vehicle.query.filter_by(id=vid).first()
        vehicle.user_id = g.user.id
        vehicle.available = False

        new_task = VehicleTask(vehicle_id=vehicle.id, user_id=g.user.id)
        db.session.add(new_task)
        db.session.commit()

    if error:
        flash(error)

    return redirect(url_for('vehicles.index'))


@bp.route('/return_vehicle', methods=('GET', 'POST'))
def return_vehicle():
    vid = request.args.get('vid')

    vehicle = Vehicle.query.filter_by(id=vid).first()
    vehicle.user_id = None
    vehicle.available = True

    task = VehicleTask.query.filter_by(
        vehicle_id=vid,
        end_time=None,
    ).order_by(VehicleTask.start_time.desc()).first()
    task.end_time = datetime.datetime.now()
    db.session.commit()

    return redirect(url_for('vehicles.index'))


@bp.route('/task_history', methods=('GET', 'POST'))
def task_history():
    vid = request.args.get('vid')

    vehicle = Vehicle.query.filter_by(id=vid).first()

    tasks = VehicleTask.query.filter_by(vehicle_id=vid).all()

    users = {
        user.id: user for user in
        User.query.filter(User.id.in_(
            [task.user_id for task in tasks]
        )).all()
    }

    return render_template('vehicles/task_history.html', vehicle=vehicle, tasks=tasks, users=users)


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
