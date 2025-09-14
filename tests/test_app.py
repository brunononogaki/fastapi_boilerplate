from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_boilerplate.app import app_test_env


def test_app_online():
    client = TestClient(app_test_env)
    response = client.get('/api/v1/health')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'status': 'healthy'}
