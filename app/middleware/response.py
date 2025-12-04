from fastapi import Request
from datetime import datetime
from typing import Any, Optional, List, Dict
from app.schemas.response import APIResponse
from app.core.enum import ResponseEnum


def build_response(
    request: Optional[Request] = None,
    *,
    data: Any = None,
    message: Optional[str] = None,
    code: int = 200,
    status: str = ResponseEnum.SUCCESS,
    errors: Optional[List[Dict[str, Any]]] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> APIResponse:
    return APIResponse(
        code=code,
        status=status,
        message=message,
        data=data,
        errors=errors,
        meta=meta,
        url=str(request.url) if request else None,
        timestamp=f"{datetime.utcnow().isoformat(timespec='seconds')}Z",
    )
