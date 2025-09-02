import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fastapi_boilerplate.app import app
from fastapi_boilerplate.core.security import create_access_token
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.crud.users import user_crud
from fastapi_boilerplate.models.base import Base
from fastapi_boilerplate.models.users import User


@pytest_asyncio.fixture
async def db_session():
    database_url = settings.test_database_url

    engine = create_async_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create the default admin user"""
    await user_crud.create_admin(db_session, settings.admin_password)
    result = await db_session.execute(select(User).filter_by(username='admin'))
    admin = result.scalar_one_or_none()
    return admin


@pytest_asyncio.fixture
async def admin_token(admin_user: User) -> str:
    """Generate a JWT Token"""
    return create_access_token(data={'sub': admin_user.username, 'user_id': str(admin_user.id)})


@pytest_asyncio.fixture
async def client(admin_token: str):
    """Create a TestClient with authenticated headers"""
    with TestClient(app) as test_client:
        # Define headers padrão com o token de autenticação
        test_client.headers.update({'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'})
        yield test_client
