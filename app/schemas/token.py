from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class TokenPayload(BaseModel):
    sub: Optional[str] = None


class TokenRefreshRequest(BaseModel):
    refresh_token: str
