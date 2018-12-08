def test_app(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'Business Portfolio' in response.data

def test_home(test_client):
    response = test_client.get('/signup')
    assert response.status_code == 200
