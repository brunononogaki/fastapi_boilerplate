import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fastapi_boilerplate.app import app
from fastapi_boilerplate.core.database import get_session
from fastapi_boilerplate.core.security import create_access_token
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.crud.users import user_crud
from fastapi_boilerplate.models.base import Base
from fastapi_boilerplate.models.users import User


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(settings.database_url_test)

    # Drop Database when starting the tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create Session and return
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    # Drop Database after finishing the tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create the default admin user"""
    await user_crud.create_admin(db_session, settings.admin_password)
    result = await db_session.execute(select(User).filter_by(username='admin'))
    admin = result.scalar()
    return admin


@pytest_asyncio.fixture
async def admin_token(admin_user: User) -> str:
    """Generate a JWT Token"""
    return create_access_token(data={'sub': admin_user.username, 'user_id': str(admin_user.id)})


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, admin_token: str):
    """Create a TestClient with authenticated headers"""

    # Override session to use the Test DB
    app.dependency_overrides[get_session] = lambda: db_session
    with TestClient(app) as test_client:
        test_client.headers.update({'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'})
        yield test_client
