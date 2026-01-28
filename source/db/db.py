from sqlalchemy import create_engine

from source.db.base import Base
from source.db.model import MarketplaceTemplate, SellerCsvUpload, Files, SellerTemplateMapping
from source.config.config import get_config

DATABASE_URL = get_config("database.url")

engine = create_engine(
    DATABASE_URL,
    echo=False  # shows logs
)


def init_db():
    Base.metadata.create_all(bind=engine)
