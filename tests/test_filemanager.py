import pytest
import os
from io import BytesIO
from flask import url_for, current_app
from carcollect.filemanager import save_file, upload
from carcollect.analyze import audiofile_upload
from werkzeug.datastructures import FileStorage


def test_upload(client, app):
	test_filename = 'test_file.txt'
	message = f'file {test_filename} uploaded successfully'
	encoded_message = message.encode('utf-8')
	data = create_testfile(test_filename.split('.')[0], test_filename.split('.')[1])
	
	response = client.get('/files/upload')
	assert response.status_code == 200
	
	response = client.post('/files/upload', data=data) 
	assert encoded_message in response.data

	with app.app_context():
		path = os.path.join(current_app.config['UPLOAD_FOLDER'], test_filename)
		assert os.path.exists(path)
		os.remove(path)


@pytest.mark.parametrize(('name', 'extension', 'message'), (
    ('test', 'txt', b'File type not allowed'),
    ('', '', b'No file found'),
    ('test', 'wav', b'file test.wav uploaded successfully')
))
def test_upload_errors(client, app, monkeypatch, name, extension, message):
	data = create_testfile(name, extension)

	class Recorder(object):
		called = False

	def fake_call():
		Recorder.called = True

	# monkeypatch.setattr('carcollect.filemanager.upload', fake_call) 
	
	with app.app_context():
		full_filename = f'{name}.{extension}'
		path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'analyze', full_filename)

		response = client.post('/analyze/upload', data=data, follow_redirects=True)
		
		assert message in response.data

		# remove testfile
		if not full_filename == '.':	
			if os.path.exists(path):
				os.remove(path)


def test_filelist(client, testaccount):
	# test redirect to login page
	response = client.get('/files/')
	assert response.status_code == 302

	#test page after logging in
	testaccount.login()
	response = client.get('/files/')
	assert response.status_code == 200


@pytest.mark.parametrize('filename', (
    '.gitignore',
    'analyze',
))
def test_file_page(client, testaccount, filename):
	testaccount.login()
	url = f'/files/{filename}'

	response = client.get(url)
	assert response.status_code == 200


def create_testfile(name='', extension=''):
	test_filename = ''
	if not name == '' and not extension == '':
		test_filename = f'{name}.{extension}'
	data = {'file': (BytesIO(b'my file contents'), test_filename),}
	return data
