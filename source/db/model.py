from sqlalchemy import (Column,BigInteger,String,DateTime,func, UniqueConstraint,ForeignKey)
from sqlalchemy.dialects.postgresql import JSONB
from source.db.base import Base 

class MarketplaceTemplate(Base):
    __tablename__ = "marketplace_templates"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    template_name = Column(
        String(100),
        nullable=False,
        index=True
    )

    version = Column(
        String(20),
        nullable=False
    )

    file_id = Column(
        BigInteger,
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
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

    __table_args__ = (
        UniqueConstraint(
            "template_name",
            "version",
            name="uq_marketplace_template_version"
        ),
    )
class SellerCsvUpload(Base):
    __tablename__ = "seller_csv_uploads"

    id = Column(BigInteger, primary_key=True)

    seller_id = Column(String, nullable=False, index=True)

    csv_file_id = Column(
        BigInteger,
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SellerTemplateMapping(Base):
    __tablename__ = "seller_template_mappings"

    id = Column(BigInteger, primary_key=True)

    seller_id = Column(String, nullable=False, index=True)

    marketplace = Column(String, nullable=False, index=True)

    template_id = Column(
        BigInteger,
        ForeignKey("marketplace_templates.id", ondelete="CASCADE"),
        nullable=False
    )

    mapping_file_id = Column(
        BigInteger,
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "seller_id",
            "template_id",
            name="uq_seller_template_mapping"
        ),
    )
    
class Files(Base):
    __tablename__ = "files"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(1024),
        nullable=False,
        unique=True
    )

    file_type = Column(
        String(10),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )