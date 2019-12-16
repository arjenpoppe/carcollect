def test_page_renders(client):
	response = client.get('/analyze/upload')
	assert response.status_code == 200

	response = client.get('/analyze/uploads')
	assert response.status_code == 200


def test_analyze_file(client):
	pass


def test_file_conversion(client, app):
	pass


def test_read_file(client):
	pass


def test_create_plot_data(client):
	pass


def test_non_audio_file(client):
	pass



# def test_allowed_extensions(client):
# 	response = client.get('/analyze/upload')
# 	assert response.data == 'Upload new File'

# def t