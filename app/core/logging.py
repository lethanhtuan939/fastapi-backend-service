import logging
import sys
import os
import time
import uuid
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.context import correlation_id, if_id, request_id
from app.core.config import settings


class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result)

    def format(self, record):
        s = super(OneLineExceptionFormatter, self).format(record)

        if record:
            s = s.replace("\r\n", "")
            s = s.replace("\n", "")
        return s


class ContextFilter(logging.Filter):
    """ "Provides correlation id parameter for the logger"""

    def filter(self, record):
        try:
            record.correlation_id = correlation_id.get()
        except LookupError:
            record.correlation_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
            
        try:
            record.if_id = str(if_id.get()).upper()
        except LookupError:
            record.if_id = "IF-0000"
            
        try:
            record.request_id = str(request_id.get()).upper()
        except LookupError:
            record.request_id = "0000"
            
        return True


# common formatter
formatter = OneLineExceptionFormatter(
    "%(asctime)-15s - [SYSTEM] - [%(if_id)s] - %(name)-5s - %(request_id)s - %(levelname)s - [%(filename)s:%(lineno)s - %(funcName)s() ] - %(message)s"
)

# root logger
# We use a broad name to capture app logs. User requested "app.fastapi.project". 
# Ensuring 'app' logs are captured.
logger = logging.getLogger("app.fastapi.project")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addFilter(ContextFilter())

# sql logger
sql_logger = logging.getLogger("sqlalchemy.engine.Engine")
sql_logger.setLevel(logging.INFO)

sql_logger.addHandler(console_handler)
sql_logger.addFilter(ContextFilter())

# log to file if local/configured
if settings.ENVIRONMENT.upper() == "LOCAL":
    log_file_path = settings.LOG_FILE_PATH
    log_dir = os.path.dirname(log_file_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        
    file_handler = logging.FileHandler(
        log_file_path, "w", encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addFilter(ContextFilter())

    sql_logger.addHandler(file_handler)
    sql_logger.addFilter(ContextFilter())

# stop delegate logs to root logger (avoid duplicate logs)
sql_logger.propagate = False
logger.propagate = False


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Set context variables
        req_id = str(uuid.uuid4())
        corr_id = uuid.uuid4()
        
        token_request_id = request_id.set(req_id[:8]) # Shorten for readability if desired, or keep full
        token_correlation_id = correlation_id.set(corr_id)
        token_if_id = if_id.set("IF-0001") # Example static/dynamic

        start_time = time.perf_counter()
        
        # Log Request
        logger.info(f"Incoming request: {request.method} {request.url}")

        try:
            response = await call_next(request)
            
            process_time = time.perf_counter() - start_time
            logger.info(
                f"Request finished: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.4f}s"
            )
            return response
        except Exception:
            process_time = time.perf_counter() - start_time
            logger.exception(
                f"Request failed: {request.method} {request.url} - Time: {process_time:.4f}s"
            )
            raise
        finally:
            # Reset tokens
            request_id.reset(token_request_id)
            correlation_id.reset(token_correlation_id)
            if_id.reset(token_if_id)
