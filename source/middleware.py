from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from source.handlers.authHandler import verify_token
import logging

logger = logging.getLogger(__name__)

UNAUTH_PATHS = {"/v1", "/v1/", "/token", "/docs", "/openapi.json"}

async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if path in UNAUTH_PATHS or path.startswith("/docs"):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authorization header missing"},
        )

    scheme, _, token = auth_header.partition(" ")
    if scheme != "Bearer" or not token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid Authorization header format"},
        )

    try:
        payload = verify_token(token)
        request.state.user = payload
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(e)},
        )

    return await call_next(request)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    readable_errors = [
        {"field": ".".join(str(x) for x in e["loc"]), "msg": e["msg"], "type": e["type"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"errors": readable_errors})