import sqlite3

import pytest
from carcollect.db import get_db


# Tests if the db connection closes after use
def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


# tests if the cli command 'init-db' gets called correctly
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('carcollect.db.init_db', fake_init_db) # connects a Recorder to the 'init-db' cli command to determine wherther it was called or not
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called