import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_boilerplate.core.security import get_password_hash, verify_password
from fastapi_boilerplate.models.users import User
from fastapi_boilerplate.schemas.users import UserCreate, UserUpdate


class UserCRUD:
    @classmethod
    def create_admin(cls, db: Session, admin_password) -> User:
        """
        Create default admin user
        """
        password = get_password_hash(admin_password)
        db_user = User(
            username='admin',
            email='admin@admin.com',
            first_name='Admin',
            last_name='User',
            password=password,
            is_admin=True,
        )

        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError('Admin account already exists')

    @classmethod
    def create_user(cls, db: Session, user_create: UserCreate) -> User:
        """
        Create a new user
        """
        password = get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            password=password,
            is_admin=user_create.is_admin,
        )

        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError('Username or email already exists')

    @classmethod
    def get_user_by_id(cls, db: Session, user_id: uuid.UUID) -> Optional[User]:
        """
        Get user by ID
        """
        return db.scalar(
            select(User).where(User.id == user_id).limit(1)
        )

    @classmethod
    def get_user_by_username(cls, db: Session, username: str) -> Optional[User]:
        """
        Get user by username
        """
        return db.scalar(
            select(User).where(User.username == username).limit(1)
        )

    @classmethod
    def get_user_by_email(cls, db: Session, email: str) -> Optional[User]:
        """
        Get user by email
        """
        return db.scalar(
            select(User).where(User.email == email).limit(1)
        )

    @classmethod
    def get_users(cls, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get list of users with pagination, ordered by username
        """
        return db.scalars(
            select(User).order_by(User.username).offset(skip).limit(limit)
        )

    @classmethod
    def get_users_count(cls, db: Session) -> int:
        """
        Get total count of Users
        """
        return db.scalar(
            select(User).count()
        )

    @classmethod
    def update_user(cls, db: Session, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
        """
        Update user information
        """
        db_user = cls.get_user_by_id(db, user_id)
        if not db_user:
            return None

        # Protect admin user from losing admin privileges
        if db_user.username == 'admin' and hasattr(user_update, 'is_admin') and user_update.is_admin is False:
            raise ValueError('Cannot remove admin privileges from the default admin user')

        update_data = user_update.dict(exclude_unset=True)

        # Protect admin user from losing admin privileges (additional check for dict access)
        if db_user.username == 'admin' and 'is_admin' in update_data and update_data['is_admin'] is False:
            raise ValueError('Cannot remove admin privileges from the default admin user')

        # Hash password if provided
        if 'password' in update_data:
            update_data['password'] = get_password_hash(update_data.pop('password'))

        try:
            for field, value in update_data.items():
                setattr(db_user, field, value)

            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError('Username or email already exists')

    @classmethod
    def delete_user(cls, db: Session, user_id: uuid.UUID) -> bool:
        """
        Delete user by ID
        """
        db_user = cls.get_user_by_id(db, user_id)
        if not db_user:
            return False

        # Protect admin user from being deleted
        if db_user.username == 'admin':
            raise ValueError('Cannot delete the default admin user')

        db.delete(db_user)
        db.commit()
        return True

    @classmethod
    def authenticate_user(cls, db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        """
        user = cls.get_user_by_username(db, username)

        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user


# Create instance
user_crud = UserCRUD()
