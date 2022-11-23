import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///av-fms.sqlite3'

    from .models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import auth
    app.register_blueprint(auth.bp)

    from . import vehicles
    app.register_blueprint(vehicles.bp)

    from . import api
    app.register_blueprint(api.bp)
    app.secret_key = api.secret_key

    return app
