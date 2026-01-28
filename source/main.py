from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from source.db.db import init_db
from source.register import registerRoutes 
from contextlib import asynccontextmanager
from constants import TEMPLATE_DIR, UPLOAD_DIR,MAPPING_UPLOAD_DIR
from pathlib import Path

def inii_dirs():
    dirs = [
        TEMPLATE_DIR,
        UPLOAD_DIR,
        MAPPING_UPLOAD_DIR,
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    inii_dirs()
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
registerRoutes(app)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    convertToReadableMessage = [
        {
            "field": ".".join(str(x) for x in e["loc"]),
            "msg": e["msg"],
            "type": e["type"]
        }
        for e in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"errors": convertToReadableMessage})