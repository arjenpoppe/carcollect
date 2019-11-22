def test_upload_file_page(client):
	response = client.get('/analyze/upload')
	assert 'Upload new File' in str(response.data)


# def test_allowed_extensions(client):
# 	response = client.get('/analyze/upload')
# 	assert response.data == 'Upload new File'