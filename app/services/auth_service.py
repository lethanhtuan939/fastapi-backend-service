from datetime import timedelta
from typing import Tuple

import jwt
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.enum import TokenType
from app.models.token import Token as TokenModel
from app.models.user import User
from app.schemas.token import Token


def save_user_token(db: Session, user: User, token_str: str, token_type: TokenType):
    # Cleanup revoked or expired tokens
    db.query(TokenModel).filter(
        TokenModel.user_id == user.u_id,
        or_(TokenModel.revoked == True, TokenModel.expired == True),
    ).delete(synchronize_session=False)

    # Enforce limit: count active tokens (using Refresh tokens as proxy for sessions)
    if token_type == TokenType.REFRESH:
        active_refresh_tokens = (
            db.query(TokenModel)
            .filter(
                TokenModel.user_id == user.u_id,
                TokenModel.token_type == TokenType.REFRESH,
            )
            .all()
        )

        if len(active_refresh_tokens) >= 2:
            # Revoke/Delete the oldest one
            oldest_token = min(active_refresh_tokens, key=lambda t: t.id)
            db.delete(oldest_token)

    db_token = TokenModel(
        user_id=user.u_id,
        token=token_str,
        token_type=token_type,
        expired=False,
        revoked=False,
    )
    db.add(db_token)
    db.commit()


def revoke_token(db: Session, token_str: str):
    token = db.query(TokenModel).filter(TokenModel.token == token_str).first()
    if token:
        db.delete(token)
        db.commit()


def authenticate_user(db: Session, username: str, password: str) -> Token:
    user = db.query(User).filter(User.u_username == username).first()
    if not user or not security.verify_password(password, user.u_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.u_username}, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(data={"sub": user.u_username})

    # Save tokens
    save_user_token(db, user, access_token, TokenType.ACCESS)
    save_user_token(db, user, refresh_token, TokenType.REFRESH)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type=TokenType.BEARER,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def refresh_access_token(db: Session, token_str: str) -> Token:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": TokenType.BEARER},
    )

    # 1. Check validity from DB
    db_token = (
        db.query(TokenModel)
        .filter(
            TokenModel.token == token_str,
            TokenModel.token_type == TokenType.REFRESH,
            TokenModel.revoked == False,
            TokenModel.expired == False,
        )
        .first()
    )

    if not db_token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = db.query(User).filter(User.u_username == username).first()
    if user is None:
        raise credentials_exception

    # 2. Delete old refresh token (Rotate)
    db.delete(db_token)
    db.commit()

    # 3. Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.u_username}, expires_delta=access_token_expires
    )
    new_refresh_token = security.create_refresh_token(data={"sub": user.u_username})

    save_user_token(db, user, access_token, TokenType.ACCESS)
    save_user_token(db, user, new_refresh_token, TokenType.REFRESH)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type=TokenType.BEARER,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def logout(db: Session, token_str: str):
    revoke_token(db, token_str)
