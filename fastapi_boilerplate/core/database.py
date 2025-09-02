from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fastapi_boilerplate import models  # noqa: F401
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.models.base import Base

engine = create_async_engine(settings.database_url)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
