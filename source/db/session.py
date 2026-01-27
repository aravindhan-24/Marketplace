from sqlalchemy.orm import sessionmaker
from source.db.db import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
