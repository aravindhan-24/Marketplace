import logging
from sqlalchemy.orm import Session
from source.db.db import SessionLocal

logger = logging.getLogger(__name__)

def get_db():
    logger.debug("Creating new database session")
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        logger.exception("Exception occurred during DB session usage")
        raise
    finally:
        db.close()
        logger.debug("Database session closed")
