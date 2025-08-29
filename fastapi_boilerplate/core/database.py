from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_boilerplate import models  # noqa: F401
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.models.base import Base

engine = create_engine(settings.database_url)


def get_session():
    with Session(engine) as session:
        yield session


def create_tables():
    Base.metadata.create_all(engine)
