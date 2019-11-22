import pytest
from flask import g, session
from carcollect.db import get_db

def test_register(client, app):
	"""Summary
	
	Args:
	    client (TYPE): Description
	    app (TYPE): Description
	"""
	assert client.get('/account/create_account').status_code == 200
	response = client.post(
		'/account/create_account', data={'firstname': 'a', 'lastname': 'p', 'email': 'a@p.com', 'password': 'test'}
	)
	assert 'http://localhost/account/login' == response.headers['Location']

	with app.app_context():
		assert get_db().execute(
			"SELECT * FROM user WHERE email = 'a@p.com'",
			).fetchone() is not None


@pytest.mark.parametrize(('firstname', 'lastname', 'email', 'password', 'message'), (
	('', '', '', '', b'First Name is required.'),
	('a', '', '', '', b'Last Name is required'),
	('a', 'p', '', '', b'Email is required'),
	('a', 'p', 'a@p.com', '', b'Password is required'),
	('test', 'account', 'test@email.com', 'test', b'Email test@email.com already exists in our database. ' \
		b'It is not possible to recover your account. Good luck remembering the password.')
))
def test_registration_input(client, firstname, lastname, email, password, message):
	response = client.post(
		'/account/create_account',
		data={'firstname':firstname, 'lastname':lastname, 'email':email, 'password':password })
	assert message in response.data


def test_login(client, testaccount):
	assert client.get('/account/login').status_code == 200
	
	response = testaccount.login()
	assert response.headers['Location'] == 'http://localhost/' 

	with client:
		client.get('/')
		assert session['user_id'] == 2
		assert g.user['email'] == 'test@email.com'


@pytest.mark.parametrize(('email', 'password', 'message'), (
    ('a', 'test', b'The combination of email and password is incorrect. Please try again.'),
))
def test_login_validate_input(client, email, password, message):
    response = client.post(
            'account/login',
            data={'email': email, 'password': password}
        )
    assert message in response.data



def test_logout(client, testaccount):
    testaccount.login()

    with client:
        testaccount.logout()
        assert 'user_id' not in session

