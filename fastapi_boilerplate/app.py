from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_boilerplate.core.database import create_tables, engine
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.crud.users import user_crud
from fastapi_boilerplate.routers import auth, users


async def create_admin_user():
    """
    Create default admin user if not created
    """
    try:
        async with AsyncSession(engine) as db:
            # Verifica se o admin já existe
            existing_admin = await user_crud.get_user_by_username(db, 'admin')

            if not existing_admin:
                await user_crud.create_admin(db, settings.admin_password)
            else:
                pass

    except Exception as e:
        logger.error(f'Error creating admin user: {e}')
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    await create_admin_user()
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

# Routers
app.include_router(auth.router, prefix='/api/v1', tags=['authentication'])
app.include_router(users.router, prefix='/api/v1', tags=['users'])


@app.get('/')
async def root():
    return {'message': 'API is running'}


@app.get('/health')
async def health_check():
    return {'status': 'healthy'}
