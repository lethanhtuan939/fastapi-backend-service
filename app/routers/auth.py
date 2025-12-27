from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_db, oauth2_scheme, get_current_user
from app.models.user import User
from app.schemas.token import Token, TokenRefreshRequest
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    return auth_service.authenticate_user(db, form_data.username, form_data.password)


@router.post("/refresh", response_model=Token)
def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db),
):
    return auth_service.refresh_access_token(db, request.refresh_token)


@router.post("/logout")
def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auth_service.logout(db, token)
    return {"msg": "Successfully logged out"}
