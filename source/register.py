import importlib
from fastapi import FastAPI
from source.routes import routes

def loadHandler(handler: str):
    modulePath, funcName = handler.split(":")
    module = importlib.import_module(modulePath)
    return getattr(module, funcName)

def registerRoutes(app: FastAPI):
    for r in routes:
        handler = loadHandler(r["handler"])

        app.add_api_route(
            path=r["path"],
            endpoint=handler,
            methods=[r["method"]],
            description=r["description"],
        )