import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi_boilerplate.core.database import create_tables
from fastapi_boilerplate.routers import auth, users

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
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
