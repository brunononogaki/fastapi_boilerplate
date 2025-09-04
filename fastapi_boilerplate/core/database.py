from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.models.base import Base

engine = create_engine(settings.database_url)


def get_session():  # pragma: no cover
    with Session(engine) as session:
        yield session


def create_tables():
    Base.metadata.create_all(engine)
