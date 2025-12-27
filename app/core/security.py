from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext
import uuid
from app.core.config import settings
from app.core.enum import TokenType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(
    data: dict,
    token_type: str,
    expires_delta: Optional[timedelta],
    default_expire_minutes: int,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=default_expire_minutes)
    to_encode.update({"exp": expire, "type": token_type, "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return _create_token(
        data, TokenType.ACCESS, expires_delta, settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return _create_token(
        data, TokenType.REFRESH, expires_delta, settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
