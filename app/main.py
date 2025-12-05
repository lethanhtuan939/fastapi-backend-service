import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import users
from app.middleware.exception_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.middleware.language import LanguageMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import logger, RequestLoggingMiddleware

app = FastAPI(
    title="Backend Service",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
)

# Setup logging
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(LanguageMiddleware)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# === Include routers ===
app.include_router(users.router)
