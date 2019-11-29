import os
import tempfile

import pytest
from carcollect import create_app
from carcollect.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def testaccount(client):
    return AccountActions(client)


class AccountActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='test@email.com', password='test'):
        return self._client.post(
            'account/login',
            data={'email': email, 'password': password}
        )

    def logout(self):
        return self._client.get('/account/logout')


