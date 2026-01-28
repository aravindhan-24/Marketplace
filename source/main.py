from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from source.initialize import initialize
from source.middleware import auth_middleware, validation_exception_handler
from source.register import registerRoutes

app = FastAPI(lifespan=initialize)

app.middleware("http")(auth_middleware)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

registerRoutes(app)