# from http import HTTPStatus

# @pytest.fixture
# def admin_user(db_session: Session) -> User:
#     """Create the default admin user"""
#     user_crud.create_admin(db_session, settings.admin_password)
#     result = db_session.execute(select(User).filter_by(username='admin'))
#     admin = result.scalar()
#     return admin

# def test_login_success(client: TestClient):
#     """Test successful login with admin"""
#     payload = {'username': 'admin', 'password': settings.admin_password}
#     # O login espera um form, não JSON
#     response = client.post(
#         '/api/v1/auth/login', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'}
#     )
#     assert response.status_code == HTTPStatus.OK
#     data = response.json()
#     assert 'access_token' in data
#     assert data['token_type'] == 'bearer'
#     assert data['expires_in'] > 0


# def test_login_invalid_credentials(client):
#     """Test unsucessful login with an invalid user"""

#     payload = {
#         'username': 'admin',
#         'password': 'wrongpassword',
#     }
#     response = client.post(
#         '/api/v1/auth/login', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'}
#     )
#     assert response.status_code == HTTPStatus.UNAUTHORIZED


# def test_get_current_user_success(client, admin_token):
#     client = TestClient(app)
#     response = client.get('/api/v1/auth/user', headers={'Authorization': f'Bearer {admin_token}'})
#     assert response.status_code == HTTPStatus.OK
#     data = response.json()
#     assert data['username'] == 'admin'


# def test_get_current_admin_user_success(client, admin_token):
#     response = client.get('/api/v1/auth/admin', headers={'Authorization': f'Bearer {admin_token}'})
#     assert response.status_code == HTTPStatus.OK
#     data = response.json()
#     assert data['is_admin'] is True


# def test_get_current_user_invalid_token(client):
#     response = client.get('/api/v1/auth/user', headers={'Authorization': 'Bearer token_invalido'})
#     assert response.status_code == HTTPStatus.UNAUTHORIZED
