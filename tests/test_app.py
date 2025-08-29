from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_boilerplate.app import app

client = TestClient(app)


def test_app_online():
    client = TestClient(app)
    response = client.get('/health')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'status': 'healthy'}
