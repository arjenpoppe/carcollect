import os

from flask import Flask, render_template
from . import db
from . import analyze


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'carcollect.sqlite'),
    )
    app.config['UPLOAD_FOLDER'] = 'carcollect/static/uploads'
    app.config['PLOT_FOLDER'] = 'carcollect/static/plots'


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # temporary index page
    @app.route('/')
    def index():
        return render_template('index.html')

    # register close_db and init_db_command with application
    db.init_app(app)

    # register blueprints
    app.register_blueprint(analyze.bp)

    return app
