from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from fastapi_boilerplate.core.database import get_session
from fastapi_boilerplate.core.security import verify_token
from fastapi_boilerplate.crud.users import user_crud
from fastapi_boilerplate.models.users import User

# Security scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/auth/login')


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    # Verify token
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Extract username from token
    username: str = payload.get('sub')
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token payload',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Get user from database
    user = user_crud.get_user_by_username(db=db, username=username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get current authenticated admin user
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin privileges required')

    return current_user
