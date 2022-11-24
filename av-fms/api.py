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


@bp.route('/vehicles', methods=['GET'])
@token_required
def vehicles_index(current_user):
    """
    This endpoint cant contain an optional 'filter' parameter in the request body of the form:
    {
        "filter": {
            "param": string,
            "value": appropriate value for the param
        }
    }
    """
    # TODO: add some pagination

    query_filter = request.get_json().get('filter')
    if not query_filter.get('param') or not query_filter.get('value'):
        vehicles = Vehicle.query.all()
    elif query_filter.get('param') not in ['manufacturer', 'license_plate_number', 'available']:
        return make_response(jsonify({"message": f'Invalid filter parameter `{query_filter.get("column")}`!'}), 400)
    else:
        try:
            if query_filter.get('param') == 'manufacturer':
                vehicles = Vehicle.query.filter_by(
                    manufacturer=query_filter.get('value')).all()
            elif query_filter.get('param') == 'license_plate_number':
                vehicles = Vehicle.query.filter_by(
                    license_plate_number=query_filter.get('value')).all()
            elif query_filter.get('param') == 'available':
                vehicles = Vehicle.query.filter_by(
                    available=query_filter.get('value')).all()
        except:
            return make_response(jsonify({"message": "Invalid filter value!"}), 400)

    users = {
        user.id: user for user in
        User.query.filter(User.id.in_(
            [vehicle.user_id for vehicle in vehicles if vehicle.user_id]
        )).all()
    }

    vs = []
    for v in vehicles:
        d = {
            "id": v.id,
            "manufacturer": v.manufacturer,
            "license_plate_number": v.license_plate_number,
            "available": v.available,
        }
        if v.available is False:
            d['taken_by'] = users[v.user_id].username
        vs.append(d)

    return make_response(jsonify({"vehicles": vs}), 200)


@bp.route('/vehicles/<int:id>/take', methods=['POST'])
@token_required
def take_vehicle(current_user, id):
    user_has_taken_vehicle = True if Vehicle.query.filter_by(
        user_id=current_user.id).first() else False
    vehicle = Vehicle.query.filter_by(id=id).first()

    if user_has_taken_vehicle:
        return make_response(jsonify(
            {"message": f'You already have taken a vehicle. A user can only take one vehicle at a time.'}),
            406)
    if not vehicle:
        return make_response(jsonify({"message": "Vehicle not found."}), 404)
    if vehicle.available is False:
        username = User.query.filter_by(id=vehicle.user_id).first().username
        return make_response(jsonify({"message": f'Vehicle is already taken by {username}.'}), 406)

    vehicle.user_id = current_user.id
    vehicle.available = False

    new_task = VehicleTask(vehicle_id=vehicle.id, user_id=g.user.id)
    db.session.add(new_task)
    db.session.commit()

    return make_response(jsonify({"message": "Vehicle taken successfully."}), 200)


@bp.route('/vehicles/<int:id>/return', methods=['POST'])
@token_required
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

    task = VehicleTask.query.filter_by(
        vehicle_id=vehicle.id,
        end_time=None,
    ).order_by(VehicleTask.start_time.desc()).first()
    task.end_time = datetime.datetime.now()
    db.session.commit()

    return make_response(jsonify({"message": "Vehicle returned successfully."}), 200)


@bp.route('/vehicles/<int:id>/create', methods=['POST'])
@token_required
def create(current_user):
    if current_user.role != 'STAFF':
        return make_response(jsonify({"message": "You are not authorized to perform this action."}), 401)

    req = request.get_json()
    man = req.get('manufacturer')
    lpn = req.get('license_plate_number')

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


@bp.route('/vehicles/<int:id>/delete', methods=['DELETE'])
@token_required
def delete(current_user):
    if current_user.role != 'STAFF':
        return make_response(jsonify({"message": "You are not authorized to perform this action."}), 401)

    vehicle = Vehicle.query.filter_by(id=id).first()

    if not vehicle:
        return make_response(jsonify({"message": "Vehicle not found."}), 404)

    db.session.delete(vehicle)
    db.session.commit()

    return make_response(jsonify({"message": "Vehicle deleted successfully."}), 200)


@bp.route('/vehicles/task_history', methods=['GET'])
@token_required
def task_history(lpn):
    """
    Note: This is not the way I would have preferred to do this. I would have preferred to have an endpoint of the structure:
        /vehicles/<int:id>/task_history
    However, the task requirements were: "The API should get a vehicle's license and return its history of availability (tasks)
    that includes the date and time and the user who caught it." Putting the license plate number in the URL would have too
    clunky for my liking, so I decided to put it in the request body instead.
    """
    lpn = request.get_json().get('license_plate_number')
    v = Vehicle.query.filter_by(license_plate_number=lpn).first()
    tasks = VehicleTask.query.filter_by(vehicle_id=v.id).all()
    users = {
        user.id: user for user in
        User.query.filter(User.id.in_(
            [task.user_id for task in tasks]
        )).all()
    }

    task_history = []
    for task in tasks:
        d = {
            "task_id": task.id,
            "taken_by": users[task.user_id].username,
            "start_time": task.start_time,
            "end_time": task.end_time,
        }
        task_history.append(d)

    return make_response(jsonify({f'task_history_for_vehicle {id}': task_history}), 200)
