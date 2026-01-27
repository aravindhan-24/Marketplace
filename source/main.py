from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from source.model.csv import csv_template
from source.db.db import init_db
from source.register import registerRoutes 
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
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