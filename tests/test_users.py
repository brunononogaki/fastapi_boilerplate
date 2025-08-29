from http import HTTPStatus
from uuid import UUID

from fastapi.testclient import TestClient

from fastapi_boilerplate.app import app


def test_users_crud_flow(client: TestClient):
    # Create user
    payload = {
        'username': 'user_test_py',
        'email': 'user_test_py@example.com',
        'first_name': 'User',
        'last_name': 'Py',
        'password': 'secret123',
    }
    r = client.post('/api/v1/users/', json=payload)
    assert r.status_code == HTTPStatus.CREATED, r.text
    data = r.json()
    assert 'id' in data
    user_id = data['id']
    # Ensure ID is a valid UUID
    UUID(user_id)

    # List users (should include created)
    r = client.get('/api/v1/users/?skip=0&limit=50')
    assert r.status_code == HTTPStatus.OK
    users = r.json()
    assert any(u['id'] == user_id for u in users)

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


def test_authentication_required(client: TestClient):
    """Testa que endpoints requerem autenticação"""
    # Criar um cliente sem autenticação
    unauthenticated_client = TestClient(app)

    # Tentar acessar endpoints sem token
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


def test_admin_user_creation_and_auth(client: TestClient):
    """Testa criação de usuário admin e autenticação"""
    # Criar usuário admin
    admin_payload = {
        'username': 'super_admin',
        'email': 'super@admin.com',
        'first_name': 'Super',
        'last_name': 'Admin',
        'password': 'admin456',
        'is_admin': True,
    }

    r = client.post('/api/v1/users/', json=admin_payload)
    assert r.status_code == HTTPStatus.CREATED

    # Verificar se foi criado como admin
    user_data = r.json()
    assert user_data['is_admin'] is True
    assert user_data['username'] == 'super_admin'
