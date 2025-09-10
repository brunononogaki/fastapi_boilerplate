from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from fastapi_boilerplate.core.auth import get_current_admin_user, get_current_user
from fastapi_boilerplate.core.database import get_session
from fastapi_boilerplate.crud.users import user_crud
from fastapi_boilerplate.models.users import User
from fastapi_boilerplate.schemas.pagination import FilterPage, PaginatedResponse
from fastapi_boilerplate.schemas.users import UserCreate, UserOut, UserUpdate
from fastapi_boilerplate.utils.pagination import create_paginated_response

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]


@router.get('/', response_model=PaginatedResponse[UserOut])
async def list_users(
    db: Session,
    current_user: CurrentAdminUser,
    filter: Annotated[FilterPage, Query()],
    # skip: Annotated[int, Query(0, ge=0)],
    # limit: Annotated[int, Query(50, ge=1, le=200)],
):
    response = user_crud.get_users(db, skip=filter.skip, limit=filter.limit)
    total_count = user_crud.get_users_count(db=db)

    return create_paginated_response(items=response, total_count=total_count, skip=filter.skip, limit=filter.limit)


@router.post('/create_admin', response_model=UserOut, status_code=201)
async def create_admin_user(password: str, db: Session):
    if user_crud.get_user_by_username(db, 'admin'):
        raise HTTPException(status_code=409, detail='Admin user already exists')

    return user_crud.create_admin(db, password)


@router.post('/', response_model=UserOut, status_code=201)
async def create_user(payload: UserCreate, db: Session, current_user: CurrentAdminUser):
    # Checagens simples de unicidade (exemplo)
    if user_crud.get_user_by_username(db, payload.username):
        raise HTTPException(status_code=409, detail='username already exists')
    if user_crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail='email already exists')

    # Delegar hashing e criação ao CRUD
    return user_crud.create_user(db, payload)


@router.get('/{user_id}', response_model=UserOut)
async def get_user(
    user_id: UUID,
    db: Session,
    current_user: CurrentAdminUser,
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    return user


@router.patch('/{user_id}', response_model=UserOut)
async def patch_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session,
    current_user: CurrentUser,
):
    # Only admin and the user can change its own data
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=401, detail='user unauthorized')

    # User is not allowed to make himself admin
    if payload.is_admin is not None and not current_user.is_admin:
        raise HTTPException(status_code=401, detail='user unauthorized')

    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    return user_crud.update_user(db, user_id, payload)


@router.delete('/{user_id}', status_code=204)
async def remove_user(
    user_id: UUID,
    db: Session,
    current_user: CurrentAdminUser,
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    user_crud.delete_user(db, user_id)
