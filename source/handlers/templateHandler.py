from sqlalchemy.orm import Session
from source.db.session import SessionLocal
from source.model.csv.csv_template import MarketPlaceTemplate 
from source.db.model import MarketplaceTemplate, Files
import uuid, os
import json
from fastapi import HTTPException,UploadFile,File
from constants import TEMPLATE_DIR

def uploadTemplate(file: UploadFile = File(...)):
    db: Session = SessionLocal()

    try:
        try:
            template_json = json.load(file.file)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON file"
            )

        try:
            templateName = template_json["templateName"]
            version = template_json["version"]
        except KeyError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field in template JSON: {e.args[0]}"
            )

        existing = (
            db.query(MarketplaceTemplate)
            .filter(
                MarketplaceTemplate.template_name == templateName,
                MarketplaceTemplate.version == version
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Template already exists for this marketplace and version"
            )

        template_uuid = str(uuid.uuid4())
        file_path = TEMPLATE_DIR / f"{template_uuid}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(template_json, f, indent=2)

        db_file = Files(
            file_name=file.filename,
            file_path=str(file_path),
            file_type="json"
        )

        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        db_template = MarketplaceTemplate(
            template_name=templateName,
            version=version,
            file_id=db_file.id
        )

        db.add(db_template)
        db.commit()
        db.refresh(db_template)

        return {
            "message": "Template uploaded successfully",
            "templateId": db_template.id,
            "fileId": db_file.id,
            "template_name": templateName,
            "version": version
        }

    finally:
        db.close()


def getTemplate(marketplace_name: str):
    db: Session = SessionLocal()

    try:
        template = (
            db.query(MarketplaceTemplate)
            .filter(MarketplaceTemplate.template_name == marketplace_name)
            .first()
        )

        if not template:
            return {"message": "Template not found"}

        file = (
            db.query(Files)
            .filter(Files.id == template.file_id)
            .first()
        )

        if not file:
            return {"message": "File not found"}

        if not os.path.exists(file.file_path):
            return {"message": "File missing on disk"}

        with open(file.file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        return {
            "marketplace": template.template_name,
            "template": content
        }

    finally:
        db.close()
