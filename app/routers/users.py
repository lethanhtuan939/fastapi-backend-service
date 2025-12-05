from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user, get_user, get_users_paginated
from app.dependencies import get_db
from app.middleware.response import build_response
from app.schemas.response import APIResponse
from app.core.messages import get_message, MessageCode
from app.core.logging import logger


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
    page_no: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    db: Session = Depends(get_db),
):
    result = get_users_paginated(db, page_no=page_no, page_size=page_size)
    return build_response(
        request=request,
        data=result["items"],
        message=get_message(MessageCode.USER_LIST_RETRIEVED, request.state.lang),
        meta={
            "total": result["total"],
            "page_no": result["page_no"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
            "has_next": result["has_next"],
            "has_prev": result["has_prev"],
        },
    )


@router.get(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    responses={404: {"model": APIResponse[None], "description": "User not found"}},
)
async def read_user(user_id: str, request: Request, db: Session = Depends(get_db)):
    logger.info(f"Fetching user with ID: {user_id}")
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return build_response(
        request=request,
        data=user,
        message=get_message(MessageCode.USER_RETRIEVED, request.state.lang),
    )
