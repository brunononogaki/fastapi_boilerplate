from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_boilerplate.app import app
from fastapi_boilerplate.core.database import get_session

# from fastapi_boilerplate.app import app
# from fastapi_boilerplate.core.database import get_session
# from fastapi_boilerplate.core.security import create_access_token
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.models.base import Base


@pytest.fixture
def db_session():
    engine = create_engine(settings.database_url_test)

    # Drop Database when starting the tests
    Base.metadata.drop_all(engine)

    # Create tables
    Base.metadata.create_all(engine)

    # Create Session and return
    with Session(engine) as session:
        yield session

    # Drop Database after finishing the tests
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session: Session):
    """Create a TestClient with authenticated headers"""

    # Override session to use the Test DB
    app.dependency_overrides[get_session] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_user(client):
    """Create the default admin user"""
    payload = {'password': str(settings.admin_password)}
    r = client.post(
        '/api/v1/users/create_admin', params=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    assert r.status_code == HTTPStatus.CREATED
    return r.json()


@pytest.fixture
def admin_token(client, admin_user):
    """Get an admin token"""
    payload = {'username': 'admin', 'password': settings.admin_password}  # ajuste para sua senha
    r = client.post('/api/v1/auth/login', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    assert r.status_code == HTTPStatus.OK
    return r.json()['access_token']
