from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_boilerplate.app import app
from fastapi_boilerplate.core.database import get_session as real_get_session
from fastapi_boilerplate.core.security import create_access_token
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.crud.users import user_crud
from fastapi_boilerplate.models.base import Base
from fastapi_boilerplate.models.users import User


@pytest.fixture
def db_session():
    database_url = settings.test_database_url

    engine = create_engine(database_url)

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    # Drop everything after running the tests
    Base.metadata.drop_all(engine)


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Create the default admin user"""
    user_crud.create_admin(db_session, settings.admin_password)
    return db_session.query(User).filter(User.username == 'admin').first()


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate a JWT Token"""
    return create_access_token(data={'sub': admin_user.username, 'user_id': str(admin_user.id)})


@pytest.fixture
def client(db_session: Session, admin_token: str) -> Generator[TestClient, None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[real_get_session] = override_get_session

    # Criar um cliente com headers de autenticação padrão
    with TestClient(app) as c:
        # Configurar headers padrão com o token admin
        c.headers.update({'Authorization': f'Bearer {admin_token}'})
        yield c

    app.dependency_overrides.clear()
