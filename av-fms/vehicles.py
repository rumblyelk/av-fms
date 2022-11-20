import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('vehicles', __name__)


@bp.route('/')
def index():
    db = get_db()
    vehicles = db.execute(
        'SELECT * FROM vehicle'
    ).fetchall()
    create_staff_user()
    return render_template('vehicles/index.html', vehicles=vehicles)


def create_staff_user():
    """
    Since this whole system is a demo, this code is here to provide a staff user for testing.
    After creating a normal user for the first time and loading the vehicles page, the ability
    to log in with a staff role with the following credentials will be available:
        username: staffUser
        password: staffpass
    """
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', ('staffUser',)
    ).fetchone()
    if user is None:
        db.execute(
            'INSERT INTO user (username, password, role) VALUES (?, ?, ?)',
            ('staffUser', generate_password_hash('staffpass'), 'STAFF')
        )
        db.commit()
