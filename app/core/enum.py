from enum import Enum


class ResponseEnum:
    SUCCESS = "success"
    ERROR = "error"


class TokenType(str, Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"
    BEARER = "bearer"
