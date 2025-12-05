# app/core/logging.py
import logging
import sys
import os
from loguru import logger
import time
from uuid import uuid4
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json


class InterceptHandler(logging.Handler):
    """Route standard library logging records through loguru, preserving level and exception info."""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """Configure global logging.

    - Intercept uvicorn/fastapi logs
    - Add a pretty console sink
    - Add a rotating JSON file sink (for ELK)
    - Set custom colors for log levels

    Returns:
        configured loguru logger
    """
    for name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False

    logger.remove()

    logger.add(
        sys.stdout,
        format="""
<green>{time:YYYY-MM-DD HH:mm:ss}</green> │ <level>{level: <8}</level> │ <blue>{name}</blue>:<cyan>{function}</cyan>:<yellow>{line}</yellow> │ <level>{message}</level>
        """.strip(),
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    os.makedirs("logs", exist_ok=True)
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
        serialize=True,
        level="INFO",
    )

    logger.level("INFO", color="<bold><blue>")
    logger.level("WARNING", color="<bold><yellow>")
    logger.level("ERROR", color="<bold><red>")
    logger.level("CRITICAL", color="<bold><red><on white>")
    logger.level("SUCCESS", color="<bold><green>")
    logger.level("DEBUG", color="<magenta>")

    return logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log incoming HTTP requests and responses.

    - Skips documentation and health endpoints.
    - Safely reads request body for POST/PUT/PATCH/DELETE and preserves it
      so downstream handlers can still access it.
    - Adds contextual request_id and user_id to logs and logs duration,
      status, client IP, and body (if available).
    """

    async def dispatch(self, request: Request, call_next):
        if any(
            request.url.path.startswith(p)
            for p in ["/docs", "/redoc", "/openapi.json", "/health"]
        ):
            return await call_next(request)

        request_id = str(uuid4())[:8]
        user_id = (
            getattr(getattr(request.state, "user", None), "u_id", "anonymous")
            if hasattr(request.state, "user")
            else "anonymous"
        )

        start_time = time.perf_counter()

        body_bytes = b""
        body_log = None
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body_str = body_bytes.decode("utf-8", errors="ignore")
                    try:
                        parsed = json.loads(body_str)
                        body_log = json.dumps(parsed, indent=2, ensure_ascii=False)
                    except:
                        body_log = body_str

                if body_log is not None:
                    request._body = body_bytes
                else:
                    body_log = {}
            except Exception as e:
                body_log = f"<error reading body: {e}>"

        with logger.contextualize(request_id=request_id, user_id=user_id):
            try:
                response = await call_next(request)
                duration = time.perf_counter() - start_time

                logger.info(
                    f"Request successful - {request.method} - {str(request.url)} - {body_log} - {response.status_code} in {duration:.4f}s",
                    method=request.method,
                    url=str(request.url),
                    status=response.status_code,
                    duration=f"{duration:.4f}s",
                    client_ip=request.client.host,
                    body=body_log,
                )
                return response

            except Exception as e:
                duration = time.perf_counter() - start_time
                logger.exception(
                    f"Request failed - {request.method} - {str(request.url)} - {body_log} - error: {e} in {duration:.4f}s",
                    method=request.method,
                    url=str(request.url),
                    duration=f"{duration:.4f}s",
                    error=str(e),
                    body=body_log,
                )
                raise


logger = setup_logging()
