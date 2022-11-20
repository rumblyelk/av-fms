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
    return render_template('vehicles/index.html', vehicles=vehicles)
