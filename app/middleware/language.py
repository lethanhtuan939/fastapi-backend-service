from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        lang = request.headers.get("lang", "vi")  # default: vi
        request.state.lang = lang
        response = await call_next(request)
        return response
