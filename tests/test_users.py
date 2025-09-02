from http import HTTPStatus
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from fastapi_boilerplate.app import app


@pytest.mark.asyncio
async def test_users_crud_flow(client):
    # Create user
    payload = {
        'username': 'test_user',
        'email': 'test_user@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'secret123',
    }
    r = client.post('/api/v1/users/', json=payload)
    assert r.status_code == HTTPStatus.CREATED, r.text
    data = r.json()
    assert 'id' in data
    user_id = data['id']
    UUID(user_id)

    # List users (should include created)
    r = client.get('/api/v1/users/?skip=0&limit=50')
    assert r.status_code == HTTPStatus.OK
    users = r.json()
    assert any(u['id'] == user_id for u in users['items'])

    # Get by id
    r = client.get(f'/api/v1/users/{user_id}')
    assert r.status_code == HTTPStatus.OK
    fetched = r.json()
    assert fetched['username'] == payload['username']

    # Update (patch)
    r = client.patch(f'/api/v1/users/{user_id}', json={'first_name': 'User2'})
    assert r.status_code == HTTPStatus.OK
    updated = r.json()
    assert updated['first_name'] == 'User2'

    # Delete
    r = client.delete(f'/api/v1/users/{user_id}')
    assert r.status_code == HTTPStatus.NO_CONTENT

    # Get should 404
    r = client.get(f'/api/v1/users/{user_id}')
    assert r.status_code == HTTPStatus.NOT_FOUND


def test_authentication_required():
    """Testa que endpoints requerem autenticação"""
    with TestClient(app) as unauthenticated_client:
        r = unauthenticated_client.get('/api/v1/users/')
        assert r.status_code == HTTPStatus.UNAUTHORIZED

        r = unauthenticated_client.post(
            '/api/v1/users/',
            json={
                'username': 'test_user',
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'password123',
            },
        )
        assert r.status_code == HTTPStatus.UNAUTHORIZED
