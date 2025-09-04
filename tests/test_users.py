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


@pytest.fixture
def user_token(client, created_user, user_payload):
    payload = {'username': user_payload['username'], 'password': user_payload['password']}
    r = client.post('/api/v1/auth/login', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    assert r.status_code == HTTPStatus.OK
    return r.json()['access_token']


@pytest.fixture
def user_payload_2():
    return {
        'username': 'test_user_2',
        'email': 'test_user_2@example.com',
        'first_name': 'Test',
        'last_name': 'User 2',
        'password': 'secret123',
    }


@pytest.fixture
def created_user_2(client, admin_token, user_payload_2):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.post('/api/v1/users/', json=user_payload_2)
    assert r.status_code == HTTPStatus.CREATED
    return r.json()


def test_create_user(client, admin_token, user_payload):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.post('/api/v1/users/', json=user_payload)
    assert r.status_code == HTTPStatus.CREATED
    data = r.json()
    assert 'id' in data


def test_create_user_duplicate_username(client, admin_token, user_payload):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.post('/api/v1/users/', json=user_payload)
    assert r.status_code == HTTPStatus.CREATED
    payload_duplicated = user_payload.copy()
    payload_duplicated['email'] = 'other_email@example.com'
    r = client.post('/api/v1/users/', json=payload_duplicated)
    assert r.status_code == HTTPStatus.CONFLICT


def test_create_user_duplicate_email(client, admin_token, user_payload):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.post('/api/v1/users/', json=user_payload)
    assert r.status_code == HTTPStatus.CREATED
    payload_duplicated = user_payload.copy()
    payload_duplicated['username'] = 'other_username'
    r = client.post('/api/v1/users/', json=payload_duplicated)
    assert r.status_code == HTTPStatus.CONFLICT


def test_list_users(client, admin_token, created_user):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.get('/api/v1/users/?skip=0&limit=50')
    assert r.status_code == HTTPStatus.OK
    users = r.json()
    assert any(u['id'] == created_user['id'] for u in users['items'])


def test_get_user_by_id(client, admin_token, created_user):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.get(f'/api/v1/users/{created_user["id"]}')
    assert r.status_code == HTTPStatus.OK
    user_data = r.json()
    assert user_data['id'] == created_user['id']


def test_update_user_as_admin(client, admin_token, created_user):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.patch(f'/api/v1/users/{created_user["id"]}', json={'first_name': 'NewName'})
    assert r.status_code == HTTPStatus.OK
    updated = r.json()
    assert updated['first_name'] == 'NewName'


def test_update_user_as_user(client, user_token, created_user):
    client.headers.update({'Authorization': f'Bearer {user_token}'})
    r = client.patch(f'/api/v1/users/{created_user["id"]}', json={'first_name': 'NewName'})
    assert r.status_code == HTTPStatus.OK
    updated = r.json()
    assert updated['first_name'] == 'NewName'


def test_update_user_as_another_user(client, user_token, created_user_2):
    client.headers.update({'Authorization': f'Bearer {user_token}'})
    r = client.patch(f'/api/v1/users/{created_user_2["id"]}', json={'first_name': 'NewName'})
    assert r.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_user(client, admin_token, created_user):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.delete(f'/api/v1/users/{created_user["id"]}')
    assert r.status_code == HTTPStatus.NO_CONTENT
    r = client.get(f'/api/v1/users/{created_user["id"]}')
    assert r.status_code == HTTPStatus.NOT_FOUND


def test_patch_unexisting_user(client, admin_token):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.patch('/api/v1/users/00000000-0000-0000-0000-000000000000', json={'first_name': 'NovoNome'})
    assert r.status_code == HTTPStatus.NOT_FOUND


def test_delete_unexisting_user(client, admin_token):
    client.headers.update({'Authorization': f'Bearer {admin_token}'})
    r = client.delete('/api/v1/users/00000000-0000-0000-0000-000000000000')
    assert r.status_code == HTTPStatus.NOT_FOUND


def test_authentication_required(client, user_payload):
    r = client.get('/api/v1/users/')
    assert r.status_code == HTTPStatus.UNAUTHORIZED
    r = client.post('/api/v1/users/', json=user_payload)
    assert r.status_code == HTTPStatus.UNAUTHORIZED
    r = client.patch('/api/v1/users/00000000-0000-0000-0000-000000000000', json={'first_name': 'NovoNome'})
    assert r.status_code == HTTPStatus.UNAUTHORIZED
    r = client.delete('/api/v1/users/00000000-0000-0000-0000-000000000000')
    assert r.status_code == HTTPStatus.UNAUTHORIZED
