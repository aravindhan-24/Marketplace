from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from source.register import registerRoutes 

app = FastAPI()

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