from sqlalchemy import (Column,BigInteger,String,DateTime,func)
from sqlalchemy.dialects.postgresql import JSONB
from source.db.base import Base 

class MarketplaceTemplate(Base):
    __tablename__ = "marketplace_templates"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    marketplace_name = Column(
        String(100),
        nullable=False
    )

    template = Column(
        JSONB,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class SellerMapping(Base):
    __tablename__ = "seller_mappings"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    seller = Column(
        String, nullable=False
    )

    marketplace = Column(
        String,
        nullable=False
    )
    
    column_mapping = Column(
        JSONB, 
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
