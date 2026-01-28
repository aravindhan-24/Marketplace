from fastapi import HTTPException, Query , UploadFile,File
from sqlalchemy.orm import Session
from source.model.mapper.mapping_request import MappingRequest 
from source.db.model import SellerCsvUpload,SellerTemplateMapping, MarketplaceTemplate, Files
from source.db.session import SessionLocal
from source.utility.fileHelper import load_json_file, read_csv_rows
from source.utility.validationHelper import validate_csv
from pathlib import Path
import os,uuid, json
from constants import MAPPING_UPLOAD_DIR, ENCODING

def mapper(seller_id: str = Query(...),template_id: int = Query(...),file: UploadFile = File(...)):
    db: Session = SessionLocal()

    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext != ".json":
            raise HTTPException(
                status_code=400,
                detail="Only JSON mapping files are supported"
            )

        template = db.query(MarketplaceTemplate).get(template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Template not found"
            )

        upload_uuid = str(uuid.uuid4())
        disk_file_name = f"{upload_uuid}{file_ext}"
        file_path = MAPPING_UPLOAD_DIR / disk_file_name

        content = file.file.read()

        try:
            json.loads(content.decode(ENCODING))
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON mapping file"
            )

        with open(file_path, "wb") as f:
            f.write(content)

        db_file = Files(
            file_name=file.filename,
            file_path=str(file_path),
            file_type="json"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        mapping = SellerTemplateMapping(
            seller_id=seller_id,
            marketplace=template.template_name,
            template_id=template.id,
            mapping_file_id=db_file.id
        )

        db.add(mapping)
        db.commit()
        db.refresh(mapping)

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
    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))
    finally:
        db.close()


def get_mappings_by_seller():
    pass

def get_mapping_by_id(id: int):
    db: Session = SessionLocal()
    try:
        mapping_record = db.query(SellerTemplateMapping).get(id)

        if not mapping_record:
            raise HTTPException(status_code=404, detail="Mapping not found")

        file = (db.query(Files)
            .filter(Files.id == mapping_record.mapping_file_id)
            .first())

        if not file or not os.path.exists(file.file_path):
            raise HTTPException(status_code=404, detail="Mapping file not found")

        with open(file.file_path, "r", encoding="utf-8") as f:
            mapping_content = json.load(f) 

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

def validate_file(seller_id: str,mapping_file_id: int):
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
            raise HTTPException(404, "Seller mapping not found")

        mapping_file = db.query(Files).get(mapping.mapping_file_id)
        if not mapping_file:
            raise HTTPException(500, "Mapping file missing")

        mapping_json = load_json_file(mapping_file.file_path).get("mapping")
        if not mapping_json:
            raise HTTPException(400, "Invalid mapping file")

        template = db.query(MarketplaceTemplate).get(mapping.template_id)
        if not template:
            raise HTTPException(404, "Template not found")

        template_file = db.query(Files).get(template.file_id)
        if not template_file:
            raise HTTPException(500, "Template file missing")

        template_json = load_json_file(template_file.file_path)
        template_fields = template_json.get("fields")
        if not template_fields:
            raise HTTPException(400, "Invalid template file")

        csv_upload = (
            db.query(SellerCsvUpload)
            .filter(SellerCsvUpload.seller_id == seller_id)
            .order_by(SellerCsvUpload.created_at.desc())
            .first()
        )

        if not csv_upload:
            raise HTTPException(404, "No CSV uploaded for seller")

        csv_file = db.query(Files).get(csv_upload.csv_file_id)
        if not csv_file:
            raise HTTPException(500, "CSV file missing")

        rows = read_csv_rows(csv_file.file_path)

        rows = [
            {k: "" if v is None else str(v).strip() for k, v in row.items()}
            for row in rows
        ]

        result = validate_csv(
            rows=rows,
            mapping=mapping_json,
            template_fields=template_fields
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
