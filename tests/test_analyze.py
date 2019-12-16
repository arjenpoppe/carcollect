import pytest

@pytest.mark.parametrize(('url', 'statuscode', 'login'),(
	('/analyze/upload', 200, False),
	('/analyze/uploads', 200, True),
	('/analyze/uploads', 302, False)
))
def test_page_renders(client, testaccount, url, statuscode, login):
	if login: testaccount.login()
	response = client.get(url)
	assert response.status_code == statuscode


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
