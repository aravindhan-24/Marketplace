import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager
from pathlib import Path

from source.db.db import init_db
from source.register import registerRoutes
from source.config.config import load_config

config = load_config()
from source.constants.constants import (
    TEMPLATE_DIR,
    UPLOAD_DIR,
    MAPPING_UPLOAD_DIR,
    LOG_FILE_PATH,
)
from source.handlers.authHandler import verify_token
from source.logger.logger import init_logger

logger = logging.getLogger(__name__)


def init_dirs():
    dirs = [
        TEMPLATE_DIR,
        UPLOAD_DIR,
        MAPPING_UPLOAD_DIR,
        Path(LOG_FILE_PATH).parent,
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_dirs()
    init_logger(LOG_FILE_PATH)
    init_db()

    logger.info("Application startup completed")
    yield


app = FastAPI(lifespan=lifespan)
registerRoutes(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    readable_errors = [
        {
            "field": ".".join(str(x) for x in e["loc"]),
            "msg": e["msg"],
            "type": e["type"],
        }
        for e in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"errors": readable_errors})


UNAUTH_PATHS = {
    "/v1",
    "/v1/",
    "/token",
    "/docs",
    "/openapi.json",
}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    if path in UNAUTH_PATHS or path.startswith("/docs"):
        return await call_next(request)

    logger.info(f"Auth check started for path: {path}")

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        logger.warning(f"Missing Authorization header for path: {path}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authorization header missing"},
        )

    scheme, _, token = auth_header.partition(" ")

    if scheme != "Bearer" or not token:
        logger.warning(f"Invalid Authorization header format for path: {path}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid Authorization header format"},
        )

    try:
        payload = verify_token(token)
        logger.info(f"Token verified successfully for path: {path}")
    except Exception as e:
        logger.error(
            f"Token verification failed for path: {path} | error: {str(e)}"
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(e)},
        )

    request.state.user = payload
    return await call_next(request)
