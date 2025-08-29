from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fastapi_boilerplate.app import app
from fastapi_boilerplate.core.database import get_session as real_get_session
from fastapi_boilerplate.core.security import create_access_token, get_password_hash
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.models.base import Base
from fastapi_boilerplate.models.users import User


@pytest.fixture(scope='session')
def engine() -> Generator:
    database_url = settings.database_url
    if not database_url:
        raise RuntimeError('DATABASE_* não configurado para testes')
    engine = create_engine(database_url, pool_pre_ping=True, future=True)
    # Criar tabelas uma vez para a suíte
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        # Não derrubamos tabelas no dev DB; em CI poderia dropar
        pass


@pytest.fixture
def db_session(engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    trans = connection.begin()

    TestingSessionLocal = sessionmaker(bind=connection, class_=Session, autoflush=False, autocommit=False, future=True)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Cria um usuário admin para os testes"""
    admin = User(
        username='test_admin',
        email='admin@test.com',
        first_name='Test',
        last_name='Admin',
        password=get_password_hash('admin123'),
        is_admin=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Gera um token JWT para o usuário admin"""
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
