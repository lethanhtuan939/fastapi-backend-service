# app/routers/users.py
from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user, get_user, get_users
from app.dependencies import get_db
from app.middleware.response import build_response
from app.schemas.response import APIResponse
from app.core.messages import get_message, MessageCode


router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[UserResponse],
)
async def create_new_user(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db),
):
    new_user = create_user(db, user)
    return build_response(
        request=request,
        data=new_user,
        message=get_message(MessageCode.USER_CREATED, request.state.lang),
        code=201,
    )


@router.get(
    "/",
    response_model=APIResponse[List[UserResponse]],
)
async def read_users(
    request: Request,
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    users = get_users(db, offset=offset, limit=limit)
    return build_response(
        request=request,
        data=users,
        message=get_message(MessageCode.USER_LIST_RETRIEVED, request.state.lang),
        meta={"total": len(users), "page": (offset // limit) + 1, "limit": limit},
    )


@router.get(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    responses={404: {"model": APIResponse[None], "description": "User not found"}},
)
async def read_user(user_id: str, request: Request, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return build_response(
        request=request,
        data=user,
        message=get_message(MessageCode.USER_RETRIEVED, request.state.lang),
    )
