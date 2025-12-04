from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.middleware.response import build_response
from app.core.messages import get_message, MessageCode
from app.core.enum import ResponseEnum


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=build_response(
            request=request,
            code=exc.status_code,
            status=ResponseEnum.ERROR,
            message=exc.detail,
        ).model_dump(exclude_none=True),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=build_response(
            request=request,
            code=422,
            status=ResponseEnum.ERROR,
            message=get_message(MessageCode.VALIDATION_ERROR),
            errors=exc.errors(),
        ).model_dump(exclude_none=True),
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=build_response(
            request=request,
            code=500,
            status=ResponseEnum.ERROR,
            message=get_message(MessageCode.INTERNAL_ERROR, request.state.lang),
            errors=[{"detail": str(exc)}],
        ).model_dump(exclude_none=True),
    )
