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
    if not g.user:
        return redirect(url_for('auth.login'))

    vehicles = Vehicle.query.all()

    return render_template('vehicles/index.html', vehicles=vehicles)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if not g.user:
        return redirect(url_for('auth.login'))
    error = None
    if g.user.role != 'STAFF':
        error = 'You do not have permission to create vehicles.'

    if request.method == 'POST':
        try:
            man = request.form['manufacturer']
            lpn = request.form['license_plate_number']

            if not man or not lpn:
                error = 'Manufacturer and license plate number are required.'
        except:
            error = 'Something went wrong.'

        if error is None:
            try:
                new_vehicle = Vehicle(man, lpn)
                db.session.add(new_vehicle)
                db.session.commit()
            except:
                error = f'Vehicle is already registered.'
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
    if not g.user:
        return redirect(url_for('auth.login'))

    error = None
    if g.user.role != 'STAFF':
        error = "You are not authorized to perform this action."

    vid = request.args.get('vid')
    vehicle = Vehicle.query.filter_by(id=vid).first()

    if not vehicle:
        error = "Vehicle not found."

    if error is None:
        try:
            db.session.delete(vehicle)
            db.session.commit()
        except:
            error = "Vehicle could not be deleted."
        else:
            return redirect(url_for('vehicles.index'))

    if error:
        flash(error)

    return render_template('vehicles/index.html')


@bp.route('/take_vehicle', methods=('GET', 'POST'))
def take_vehicle():
    if not g.user:
        return redirect(url_for('auth.login'))

    error = None
    if g.user.vehicle:
        error = f'You already have taken the {g.user.vehicle.manufacturer} | {g.user.vehicle.license_plate_number}.'

    try:
        vid = request.args.get('vid')
        vehicle = Vehicle.query.filter_by(id=vid).first()
        vehicle.user_id = g.user.id
        vehicle.available = False

        new_task = VehicleTask(vehicle_id=vehicle.id, user_id=g.user.id)
        db.session.add(new_task)
        db.session.commit()
    except:
        error = 'Something went wrong.'
    else:
        return redirect(url_for('vehicles.index'))

    if error:
        flash(error)

    return redirect(url_for('vehicles.index'))


@bp.route('/return_vehicle', methods=('GET', 'POST'))
def return_vehicle():
    if not g.user:
        return redirect(url_for('auth.login'))

    error = None
    try:
        vid = request.args.get('vid')
        vehicle = Vehicle.query.filter_by(id=vid).first()
    except:
        error = 'Vehicle not found.'
    if vehicle.available:
        error = f'Vehicle is already available.'
    if g.user.id != vehicle.user_id:
        error = 'You can only return your own vehicle.'

    if error is None:
        vehicle.user_id = None
        vehicle.available = True

        task = VehicleTask.query.filter_by(
            vehicle_id=vid,
            end_time=None,
        ).order_by(VehicleTask.start_time.desc()).first()
        task.end_time = datetime.datetime.now()
        db.session.commit()

    if error:
        flash(error)

    return redirect(url_for('vehicles.index'))


@bp.route('/task_history', methods=('GET', 'POST'))
def task_history():
    if not g.user:
        return redirect(url_for('auth.login'))

    error = None
    try:
        vid = request.args.get('vid')
        tasks = VehicleTask.query.filter_by(vehicle_id=vid).all()
        vehicle = Vehicle.query.filter_by(id=vid).first()
    except:
        error = 'Vehicle not found.'

    if error:
        flash(error)

    return render_template('vehicles/task_history.html', tasks=tasks, vehicle=vehicle)
