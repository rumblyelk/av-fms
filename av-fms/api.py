import datetime
import functools
import secrets

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, make_response
)

import jwt

from flask_httpauth import HTTPBasicAuth

from werkzeug.security import check_password_hash, generate_password_hash

from .models import db, User, Vehicle, VehicleTask


bp = Blueprint('api', __name__, url_prefix='/api')
# secret_key = secrets.token_hex(16)
secret_key = "hello"


@bp.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic-realm= "Login required!"'})

    user = User.query.filter_by(username=auth['username']).first()
    if not user:
        return make_response('Could not verify user, Please signup!', 401, {'WWW-Authenticate': 'Basic-realm= "No user found!"'})

    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({'user_id': user.id}, secret_key, 'HS256')
        return make_response(jsonify({'token': token}), 201)

    return make_response('Could not verify password!', 403, {'WWW-Authenticate': 'Basic-realm= "Wrong Password!"'})


def token_required(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return make_response(jsonify({"message": "Invalid token!", "token": token}), 401)
        return f(current_user, *args, **kwargs)
    return decorator


@bp.route('/register', methods=['POST'])
def register():
    """
    This endpoint takes a username and password in the message body and creates a new user in the database. The message body should look like:
    {
        "username": string,
        "password": string
    }
    """
    create_staff_user()

    try:
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        if not username or not password:
            return make_response(jsonify({"message": "Username and password are required!"}), 400)
    except:
        return make_response(jsonify({"message": "Improperly formatted request body!"}), 400)

    try:
        user = User(username=username,
                    password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
    except Exception:
        return make_response(jsonify({"message": "User already exists."}), 400)

    return make_response(jsonify({"message": "User created successfully."}), 201)


@bp.route('/vehicles', methods=['GET'])
@token_required
def vehicles_index(current_user):
    """
    This endpoint cant contain an optional 'filter' parameter in the request body of the form:
    {
       "filter": {
            "manufacturer": string,
            "license_plate_number": string,
            "available": bool
        }
    }
    """
    # TODO: add some pagination (or find out if Flask autopaginates)

    try:
        filters = request.get_json().get('filter')
    except:
        filters = None

    if filters:
        if filters.keys() - {'manufacturer', 'license_plate_number', 'available'}:
            return make_response(jsonify({"message": "Invalid filter!"}), 400)

        vehicles = Vehicle.query.filter_by(**filters).all()
    else:
        vehicles = Vehicle.query.all()

    vs = [{
        "id": v.id,
        "manufacturer": v.manufacturer,
        "license_plate_number": v.license_plate_number,
        "available": v.available,
        "taken_by": v.user.username if v.available is False else None
    } for v in vehicles]

    return make_response(jsonify({"vehicles": vs}), 200)


@ bp.route('/vehicles/<int:id>/take', methods=['POST'])
@ token_required
def take_vehicle(current_user, id):
    vehicle = Vehicle.query.filter_by(id=id).first()

    if current_user.vehicle:
        return make_response(jsonify(
            {"message": f'You already have taken a vehicle. A user can only take one vehicle at a time.'}),
            406)
    if not vehicle:
        return make_response(jsonify({"message": "Vehicle not found."}), 404)
    if vehicle.available is False:
        return make_response(jsonify({"message": f'Vehicle is already taken by {vehicle.user.username}.'}), 406)

    vehicle.user_id = current_user.id
    vehicle.available = False

    new_task = VehicleTask(vehicle_id=vehicle.id, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()

    return make_response(jsonify({"message": "Vehicle taken successfully."}), 200)


@ bp.route('/vehicles/<int:id>/return', methods=['POST'])
@ token_required
def return_vehicle(current_user, id):
    vehicle = Vehicle.query.filter_by(id=id).first()

    if not vehicle:
        return make_response(jsonify({"message": "Vehicle not found."}), 404)
    if vehicle.available is True:
        return make_response(jsonify({"message": "Vehicle is already available."}), 406)
    if vehicle.user_id != current_user.id:
        return make_response(jsonify({"message": "You can only return your own vehicle."}), 406)

    vehicle.user_id = None
    vehicle.available = True

    # The reason that I kept this query instead of something like `vehicle.tasks[-1] is because the order of
    # the tasks is not guaranteed. Ordering as part of the query is more efficient than sorting in Python.
    task = VehicleTask.query.filter_by(
        vehicle_id=vehicle.id,
        end_time=None,
    ).order_by(VehicleTask.start_time.desc()).first()
    task.end_time = datetime.datetime.now()
    db.session.commit()

    return make_response(jsonify({"message": "Vehicle returned successfully."}), 200)


@ bp.route('/vehicles/create', methods=['POST'])
@ token_required
def create(current_user):
    if current_user.role != 'STAFF':
        return make_response(jsonify({"message": "You are not authorized to perform this action."}), 401)

    try:
        man = request.get_json().get('manufacturer')
        lpn = request.get_json().get('license_plate_number')

        if not man or not lpn:
            return make_response(jsonify({"message": "Request body must contain manufacturer and license_plate_number."}), 400)
    except:
        return make_response(jsonify({"message": "Improperly formatted request body!"}), 400)

    vehicle = Vehicle.query.filter_by(
        manufacturer=man, license_plate_number=lpn
    ).first()

    if vehicle:
        return make_response(jsonify({"message": "Vehicle already exists."}), 406)

    new_vehicle = Vehicle(
        manufacturer=man,
        license_plate_number=lpn,
    )
    db.session.add(new_vehicle)
    db.session.commit()

    return make_response(jsonify({"message": "Vehicle created successfully."}), 200)


@ bp.route('/vehicles/<int:id>/delete', methods=['DELETE'])
@ token_required
def delete(current_user, id):
    if current_user.role != 'STAFF':
        return make_response(jsonify({"message": "You are not authorized to perform this action."}), 401)

    vehicle = Vehicle.query.filter_by(id=id).first()

    if not vehicle:
        return make_response(jsonify({"message": "Vehicle not found."}), 404)

    db.session.delete(vehicle)
    db.session.commit()

    return make_response(jsonify({"message": "Vehicle deleted successfully."}), 200)


@ bp.route('/vehicles/task_history', methods=['GET'])
@ token_required
def task_history(lpn):
    """
    Note: This is not the way I would have preferred to do this. I would have preferred to have an endpoint of the structure:
        /vehicles/<int:id>/task_history
    However, the task requirements were: "The API should get a vehicle's license and return its history of availability (tasks)
    that includes the date and time and the user who caught it." Putting the license plate number in the URL would have too
    clunky for my liking, so I decided to put it in the request body instead.
    """
    try:
        lpn = request.get_json().get('license_plate_number')

        if not lpn:
            return make_response(jsonify({"message": "Request body must contain license_plate_number."}), 400)
    except:
        return make_response(jsonify({"message": "Improperly formatted request body!"}), 400)

    vehicle = Vehicle.query.filter_by(license_plate_number=lpn).first()

    if not vehicle:
        return make_response(jsonify({"message": "Vehicle not found."}), 404)

    task_history = [{
        "task_id": task.id,
        "taken_by": task.user.username,
        "start_time": task.start_time,
        "end_time": task.end_time,
    } for task in vehicle.tasks]

    return make_response(jsonify({"task_history": task_history}), 200)


def create_staff_user():
    """
    Since this whole system is a demo, this code is here to provide a staff user for testing.
    After starting the app for the first time, the ability to log in with a staff role with
    the following credentials will be available:
        username: staffUser
        password: staffpass
    """
    staff_user = User.query.filter_by(username='staffUser').first()

    if staff_user is None:
        staff_user = User(username='staffUser', password=generate_password_hash(
            'staffpass'), role='STAFF')
        db.session.add(staff_user)
        db.session.commit()
