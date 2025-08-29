from datetime import datetime, timedelta
from typing import Optional

# from jose import JWTError
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError, decode, encode
from pwdlib import PasswordHash

from fastapi_boilerplate.core.settings import settings

# Password hashing context
pwd_context = PasswordHash.recommended()


def verify_password(plain_password: str, password: str) -> bool:
    """
    Verify a plain password against its hash
    """
    return pwd_context.verify(plain_password, password)


def get_password_hash(password: str) -> str:
    """
    Generate password hash
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except (InvalidTokenError, ExpiredSignatureError, DecodeError):
        return None
