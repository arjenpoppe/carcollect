import sqlite3
import random

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command('fill-db')
@with_appcontext
def fill_db(rows=500000):
    init_db()
    db = get_db()

    for n in range(rows):
        filename = '{}{}{}'.format("testfile_", n, ".wav")
        severity = random.randint(0, 10)
        probability = random.randint(0, 100)

        db.execute(
            'INSERT INTO result (filename, severity, probability) VALUES (?, ?, ?)',
            (filename, severity, probability)
        )
    db.commit()
    click.echo("Database filled with random data")


@click.command('test-db')
@with_appcontext
def get_random_db_entry():
    db = get_db()
    testdata = db.execute('SELECT * FROM result WHERE filename = ?', ('testfile_{}.wav'.format(random.randint(0, 200)),)).fetchone()
    click.echo('filename: {}, severity: {}, probability: {}'.format(testdata['filename'], testdata['severity'], testdata['probability']))


def get_from_database(table, columns="*", where=None, param=None):

    db = get_db()
    data = db.execute('SELECT')





    return None

