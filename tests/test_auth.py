from http import HTTPStatus

import pytest


@pytest.fixture
def user_payload():
    return {
        'username': 'test_user',
        'email': 'test_user@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'secret123',
    }


@pytest.fixture
def created_user(client, admin_token, user_payload):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.post('/api/v1/users/', json=user_payload)
    assert r.status_code == HTTPStatus.CREATED
    return r.json()


def test_login_success(client, user_payload, created_user):
    """Test successful login with admin"""
    payload = {'username': user_payload['username'], 'password': user_payload['password']}

    response = client.post(
        '/api/v1/auth/login', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'
    assert data['expires_in'] > 0


def test_login_invalid_credentials(client, user_payload, created_user):
    """Test unsucessful login with an invalid user"""

    payload = {'username': user_payload['username'], 'password': 'wrongpassword'}
    response = client.post(
        '/api/v1/auth/login', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_current_user_success(client, user_payload, created_user):
    payload = {'username': user_payload['username'], 'password': user_payload['password']}
    response = client.post(
        '/api/v1/auth/login', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    data = response.json()
    response = client.get('/api/v1/auth/user', headers={'Authorization': f'Bearer {data["access_token"]}'})
    assert response.status_code == HTTPStatus.OK


def test_get_current_admin_user_success(client, admin_token):
    response = client.get('/api/v1/auth/admin', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['is_admin'] is True


def test_refresh_token(client, user_payload, created_user):
    """Test successful login with admin"""
    payload = {'username': user_payload['username'], 'password': user_payload['password']}

    response = client.post(
        '/api/v1/auth/login', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    response = client.post(
        '/api/v1/auth/refresh_token', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'
    assert data['expires_in'] > 0
