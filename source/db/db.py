from sqlalchemy import create_engine

from source.db.base import Base
from source.db.model import MarketplaceTemplate, SellerCsvUpload, Files, SellerTemplateMapping
import os 

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(
    DATABASE_URL,
    echo=False  # shows logs
)


def init_db():
    Base.metadata.create_all(bind=engine)
