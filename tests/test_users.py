from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fastapi_boilerplate.app import app
from fastapi_boilerplate.core.database import get_session


class TestUser:
    payload = {
        'username': 'test_user',
        'email': 'test_user@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'secret123',
    }


user = TestUser()


def test_user_crud_flow(client: TestClient):
    """Test entire users flow (create, read, update and delete)"""

    # Create user

    r = client.post('/api/v1/users/', json=user.payload)
    assert r.status_code == HTTPStatus.CREATED, r.text
    data = r.json()
    assert 'id' in data
    user.id = data['id']

    # List users (should include created)
    r = client.get('/api/v1/users/?skip=0&limit=50')
    assert r.status_code == HTTPStatus.OK
    users = r.json()
    assert any(u['id'] == user.id for u in users['items'])

    # Get created user
    r = client.get(f'/api/v1/users/{user.id}')
    assert r.status_code == HTTPStatus.OK
    users = r.json()
    assert user.id == users['id']

    # Update (patch)
    r = client.patch(f'/api/v1/users/{user.id}', json={'first_name': 'User2'})
    assert r.status_code == HTTPStatus.OK
    updated = r.json()
    assert updated['first_name'] == 'User2'

    # Delete
    r = client.delete(f'/api/v1/users/{user.id}')
    assert r.status_code == HTTPStatus.NO_CONTENT

    # Get should 404
    r = client.get(f'/api/v1/users/{user.id}')
    assert r.status_code == HTTPStatus.NOT_FOUND


def test_authentication_required(db_session: Session):
    """Test endpoints that requuires autentication"""

    # Override session to use the Test DB
    app.dependency_overrides[get_session] = lambda: db_session

    with TestClient(app) as unauthenticated_client:
        r = unauthenticated_client.get('/api/v1/users/')
        assert r.status_code == HTTPStatus.UNAUTHORIZED

        r = unauthenticated_client.post('/api/v1/users/', json=user.payload)
        assert r.status_code == HTTPStatus.UNAUTHORIZED

        r = unauthenticated_client.patch(f'/api/v1/users/{user.id}', json={'first_name': 'User2'})
        assert r.status_code == HTTPStatus.UNAUTHORIZED

        r = unauthenticated_client.delete(f'/api/v1/users/{user.id}')
        assert r.status_code == HTTPStatus.UNAUTHORIZED
