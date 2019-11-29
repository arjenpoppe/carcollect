import os

from flask import Flask, render_template
from datetime import timedelta

from . import filemanager
from . import sort
from . import analyze
from . import account
from . import db

from carcollect.db import get_db


def create_app(test_config=None):
    """App factory. Creates and configures the app, creates the default directories, registers cli commands
    to app and registers blueprints to app
    
    Args:
        test_config (None, optional): conftest will use this to override default config
    
    Returns:
        Flask App: the actual app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.permanent_session_lifetime = timedelta(minutes=30)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'carcollect.sqlite'),
    )
    app.config['UPLOAD_FOLDER'] = os.path.normpath('carcollect/static/uploads')
    app.config['PLOT_FOLDER'] = 'carcollect/static/plots'

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # create instance folder
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # some test routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # register close_db and init_db_command with application
    db.init_app(app)

    # register blueprints
    app = register_blueprints(app)

    return app


def register_blueprints(app):
    """Register blueprints to app, then return it
    
    Args:
        app (Flask app): app provided by app factory
    
    Returns:
        Flask app: app with now registered blueprints
    """
    app.register_blueprint(analyze.bp)
    app.register_blueprint(sort.bp)
    app.register_blueprint(filemanager.bp)
    app.register_blueprint(account.bp)

    return app

