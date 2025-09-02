import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from fastapi_boilerplate.app import app
from fastapi_boilerplate.core.database import get_session
from fastapi_boilerplate.core.security import create_access_token
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.crud.users import user_crud
from fastapi_boilerplate.models.base import Base
from fastapi_boilerplate.models.users import User


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
def admin_user(db_session: Session) -> User:
    """Create the default admin user"""
    user_crud.create_admin(db_session, settings.admin_password)
    result = db_session.execute(select(User).filter_by(username='admin'))
    admin = result.scalar()
    return admin


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate a JWT Token"""
    return create_access_token(data={'sub': admin_user.username, 'user_id': str(admin_user.id)})


@pytest.fixture
def client(db_session: Session, admin_token: str):
    """Create a TestClient with authenticated headers"""

    # Override session to use the Test DB
    app.dependency_overrides[get_session] = lambda: db_session
    with TestClient(app) as test_client:
        test_client.headers.update({'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'})
        yield test_client
