from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from sqlalchemy.orm import Session

from fastapi_boilerplate.core.database import create_tables, engine
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.crud.users import user_crud
from fastapi_boilerplate.routers import auth, health, users


def create_admin_user():  # pragma: no cover
    """
    Create default admin user if not created
    """
    try:
        with Session(engine) as db:
            # Verifica se o admin já existe
            existing_admin = user_crud.get_user_by_username(db, 'admin')

            if not existing_admin:
                user_crud.create_admin(db, settings.admin_password)
            else:
                pass

    except Exception as e:
        logger.error(f'Error creating admin user: {e}')
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    create_admin_user()
    yield
    # Shutdown


app = FastAPI(
    title='FastAPI Boilerplate',
    description='My basic API',
    version='1.0.0',
    lifespan=lifespan,
    swagger_ui_parameters={
        'persistAuthorization': True,
    },
)

app_test_env = FastAPI(
    title='FastAPI Boilerplate',
    description='My basic API',
    version='1.0.0',
    swagger_ui_parameters={
        'persistAuthorization': True,
    },
)


# Routers
def register_routers(app):
    app.include_router(health.router, prefix='/api/v1', tags=['health'])
    app.include_router(auth.router, prefix='/api/v1', tags=['authentication'])
    app.include_router(users.router, prefix='/api/v1', tags=['users'])


register_routers(app)
register_routers(app_test_env)
