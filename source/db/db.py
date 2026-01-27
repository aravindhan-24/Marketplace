from sqlalchemy import create_engine

from source.db.base import Base
from source.db.model import MarketplaceTemplate, SellerMapping

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/streamoid"

engine = create_engine(
    DATABASE_URL,
    echo=True  # shows logs
)


def init_db():
    print(Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
