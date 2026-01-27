from sqlalchemy.orm import Session
from source.db.db import SessionLocal

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
