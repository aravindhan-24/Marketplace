import logging

logger = logging.getLogger(__name__)

def ping():
    logger.debug("Ping endpoint called")
    return {"message": "ok"}
