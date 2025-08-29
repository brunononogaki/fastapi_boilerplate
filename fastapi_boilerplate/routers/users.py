from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from fastapi_boilerplate.core.auth import get_current_admin_user
from fastapi_boilerplate.core.database import get_session
from fastapi_boilerplate.crud.users import user_crud
from fastapi_boilerplate.models.users import User
from fastapi_boilerplate.schemas.users import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=list[UserOut])
async def list_users(
    db: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_admin_user),
):
    return user_crud.get_users(db, skip=skip, limit=limit)


@router.post('/', response_model=UserOut, status_code=201)
async def create_user(
    payload: UserCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
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
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    return user


@router.patch('/{user_id}', response_model=UserOut)
async def patch_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    return user_crud.update_user(db, user_id, payload)


@router.delete('/{user_id}', status_code=204)
async def remove_user(
    user_id: UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    user_crud.delete_user(db, user_id)
