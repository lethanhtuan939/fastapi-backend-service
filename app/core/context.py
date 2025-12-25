import uuid
from contextvars import ContextVar

# Context variables
correlation_id: ContextVar[uuid.UUID] = ContextVar(
    "correlation_id", default=uuid.UUID("00000000-0000-0000-0000-000000000000")
)

if_id: ContextVar[str] = ContextVar("if_id", default="IF-0000")

request_id: ContextVar[str] = ContextVar("request_id", default="0000")
