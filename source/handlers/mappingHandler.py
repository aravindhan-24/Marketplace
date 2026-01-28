import logging
import json
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session

from source.model.mapper.mapping_request import MappingRequest
from source.db.model import (
    SellerCsvUpload,
    SellerTemplateMapping,
    MarketplaceTemplate,
    Files,
)
from source.db.session import SessionLocal
from source.utility.fileHelper import load_json_file, read_csv_rows
from source.utility.validationHelper import validate_csv
from source.constants.constants import MAPPING_UPLOAD_DIR, ENCODING

logger = logging.getLogger(__name__)


def mapper(
    seller_id: str = Query(...),
    template_id: int = Query(...),
    file: UploadFile = File(...)
):
    logger.info(
        f"Mapping upload started | seller_id={seller_id} | template_id={template_id} | filename={file.filename}"
    )

    db: Session = SessionLocal()
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext != ".json":
            logger.warning("Invalid mapping file type uploaded")
            raise HTTPException(
                status_code=400,
                detail="Only JSON mapping files are supported"
            )

        template = db.query(MarketplaceTemplate).get(template_id)
        if not template:
            logger.warning(f"Template not found | template_id={template_id}")
            raise HTTPException(
                status_code=404,
                detail="Template not found"
            )

        upload_uuid = str(uuid.uuid4())
        file_path = MAPPING_UPLOAD_DIR / f"{upload_uuid}{file_ext}"

        content = file.file.read()

        try:
            json.loads(content.decode(ENCODING))
        except Exception:
            logger.warning("Invalid JSON mapping file uploaded")
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON mapping file"
            )

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Mapping file saved to disk | path={file_path}")

        db_file = Files(
            file_name=file.filename,
            file_path=str(file_path),
            file_type="json"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        logger.info(f"Mapping file DB record created | file_id={db_file.id}")

        mapping = SellerTemplateMapping(
            seller_id=seller_id,
            marketplace=template.template_name,
            template_id=template.id,
            mapping_file_id=db_file.id
        )

        db.add(mapping)
        db.commit()
        db.refresh(mapping)

        logger.info(
            f"Seller template mapping created | mapping_id={mapping.id} | seller_id={seller_id}"
        )

        return {
            "status": "success",
            "mapping_id": mapping.id,
            "mapping_file_id": db_file.id,
            "template_id": template.id,
            "marketplace": template.template_name
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Unexpected error during mapping upload")
        raise HTTPException(500, "Internal server error")
    finally:
        db.close()
        logger.debug("DB session closed for mapping upload")


def get_mappings_by_seller(seller_id: str = Query(...)):
    logger.info(f"Fetching mappings for seller | seller_id={seller_id}")

    db: Session = SessionLocal()
    try:
        results = (
            db.query(SellerTemplateMapping, Files)
            .join(Files, SellerTemplateMapping.mapping_file_id == Files.id)
            .filter(SellerTemplateMapping.seller_id == seller_id)
            .all()
        )

        if not results:
            logger.warning(f"No mappings found for seller | seller_id={seller_id}")
            raise HTTPException(
                status_code=404,
                detail="No mappings found for this seller"
            )

        response = []

        for mapping, file in results:
            file_path = Path(file.file_path)

            if not file_path.exists():
                logger.error(f"Mapping file missing on disk | file={file.file_name}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Mapping file missing on disk: {file.file_name}"
                )

            try:
                with open(file_path, "r", encoding=ENCODING) as f:
                    mapping_json = json.load(f)
            except Exception:
                logger.exception(f"Failed to read mapping file | file={file.file_name}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to read mapping file: {file.file_name}"
                )

            response.append({
                "mapping_id": mapping.id,
                "seller_id": mapping.seller_id,
                "marketplace": mapping.marketplace,
                "template_id": mapping.template_id,
                "mapping": mapping_json
            })

        logger.info(
            f"Mappings fetched successfully | seller_id={seller_id} | count={len(response)}"
        )

        return {
            "status": "success",
            "count": len(response),
            "data": response
        }

    finally:
        db.close()
        logger.debug("DB session closed for get_mappings_by_seller")


def get_mapping_by_id(id: int):
    logger.info(f"Fetching mapping by id | mapping_id={id}")

    db: Session = SessionLocal()
    try:
        mapping_record = db.query(SellerTemplateMapping).get(id)

        if not mapping_record:
            logger.warning(f"Mapping not found | mapping_id={id}")
            raise HTTPException(status_code=404, detail="Mapping not found")

        file = (
            db.query(Files)
            .filter(Files.id == mapping_record.mapping_file_id)
            .first()
        )

        if not file or not os.path.exists(file.file_path):
            logger.error(f"Mapping file missing | mapping_id={id}")
            raise HTTPException(status_code=404, detail="Mapping file not found")

        with open(file.file_path, "r", encoding=ENCODING) as f:
            mapping_content = json.load(f)

        logger.info(f"Mapping fetched successfully | mapping_id={id}")

        return {
            "status": "success",
            "data": {
                "id": mapping_record.id,
                "seller": mapping_record.seller_id,
                "marketplace": mapping_record.marketplace,
                "mapping": mapping_content,
                "created_at": mapping_record.created_at
            }
        }

    finally:
        db.close()
        logger.debug("DB session closed for get_mapping_by_id")

def validate_file(seller_id: str, mapping_file_id: int):
    logger.info(
        f"CSV validation started | seller_id={seller_id} | mapping_file_id={mapping_file_id}"
    )

    db: Session = SessionLocal()
    try:
        mapping = (
            db.query(SellerTemplateMapping)
            .filter(
                SellerTemplateMapping.seller_id == seller_id,
                SellerTemplateMapping.mapping_file_id == mapping_file_id
            )
            .first()
        )

        if not mapping:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Seller mapping not found")

        mapping_file = db.query(Files).get(mapping.mapping_file_id)
        if not mapping_file:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Mapping file missing")

        mapping_json = load_json_file(mapping_file.file_path).get("mapping")
        if not mapping_json:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid mapping file")

        template = db.query(MarketplaceTemplate).get(mapping.template_id)
        if not template:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

        template_file = db.query(Files).get(template.file_id)
        if not template_file:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Template file missing")

        template_json = load_json_file(template_file.file_path)
        template_fields = template_json.get("fields")
        if not template_fields:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid template file")

        csv_upload = (
            db.query(SellerCsvUpload)
            .filter(SellerCsvUpload.seller_id == seller_id)
            .order_by(SellerCsvUpload.created_at.desc())
            .first()
        )

        if not csv_upload:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No CSV uploaded for seller")

        csv_file = db.query(Files).get(csv_upload.csv_file_id)
        if not csv_file:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "CSV file missing")

        rows = read_csv_rows(csv_file.file_path)
        rows = [
            {k: "" if v is None else str(v).strip() for k, v in row.items()}
            for row in rows
        ]

        try:
            result = validate_csv(
                rows=rows,
                mapping=mapping_json,
                template_fields=template_fields
            )
        except ValueError as e:
            logger.warning(
                f"CSV validation failed | seller_id={seller_id} | reason={str(e)}"
            )
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except KeyError as e:
            logger.error(
                f"Template configuration error | missing key={e}"
            )
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Template configuration error: missing {e}"
            )
        except Exception as e:
            logger.exception("Unexpected CSV validation error")
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal validation error"
            )

        logger.info(
            f"CSV validation completed | seller_id={seller_id} | total={len(result)} | "
            f"valid={sum(r['valid'] for r in result)}"
        )

        return {
            "seller_id": seller_id,
            "mapping_file_id": mapping_file_id,
            "total": len(result),
            "valid": sum(r["valid"] for r in result),
            "errors": result
        }

    finally:
        db.close()
        logger.debug("DB session closed for validate_file")
