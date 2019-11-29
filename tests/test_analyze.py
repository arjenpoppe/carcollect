def test_convert_mp3(client):
	response = client.get('/analyze/upload')
	assert response.status_code == 200

def test_analyze_file(client):
	pass




# def test_allowed_extensions(client):
# 	response = client.get('/analyze/upload')
# 	assert response.data == 'Upload new File'

# def t