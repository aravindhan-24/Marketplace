import logging
import importlib
from fastapi import FastAPI
from source.routes import routes

logger = logging.getLogger(__name__)


def loadHandler(handler: str):
    logger.debug(f"Loading handler | handler={handler}")

    try:
        modulePath, funcName = handler.split(":")
        module = importlib.import_module(modulePath)
        return getattr(module, funcName)
    except Exception:
        logger.exception(f"Failed to load handler | handler={handler}")
        raise


def registerRoutes(app: FastAPI):
    logger.info("Registering API routes")

    for r in routes:
        handler = loadHandler(r["handler"])

        app.add_api_route(
            path=r["path"],
            endpoint=handler,
            methods=[r["method"]],
            description=r["description"],
        )

        logger.info(
            f"Route registered | {r['method']} {r['path']} -> {r['handler']}"
        )
