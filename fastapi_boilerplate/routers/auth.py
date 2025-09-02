from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_boilerplate.core.database import get_session
from fastapi_boilerplate.core.security import create_access_token
from fastapi_boilerplate.core.settings import settings
from fastapi_boilerplate.crud.users import user_crud
from fastapi_boilerplate.schemas.auth import TokenResponse

router = APIRouter()


@router.post('/auth/login', response_model=TokenResponse)
async def login(login_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    """
    Authenticate user and return JWT token
    """
    # Authenticate user
    user = await user_crud.authenticate_user(db=db, username=login_data.username, password=login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={'sub': user.username, 'user_id': str(user.id)}, expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token, token_type='bearer', expires_in=settings.access_token_expire_minutes
    )
