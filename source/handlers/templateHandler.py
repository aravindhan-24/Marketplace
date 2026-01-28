import logging
import uuid
import os
import json

from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, File

from source.db.session import SessionLocal
from source.db.model import MarketplaceTemplate, Files
from source.constants.constants import TEMPLATE_DIR

logger = logging.getLogger(__name__)


def uploadTemplate(file: UploadFile = File(...)):
    logger.info(f"Template upload started | filename={file.filename}")

    db: Session = SessionLocal()
    try:
        try:
            template_json = json.load(file.file)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON uploaded for template")
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON file"
            )

        try:
            templateName = template_json["templateName"]
            version = template_json["version"]
        except KeyError as e:
            logger.warning(f"Missing required field in template JSON | field={e.args[0]}")
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
            logger.warning(
                f"Template already exists | marketplace={templateName} | version={version}"
            )
            raise HTTPException(
                status_code=409,
                detail="Template already exists for this marketplace and version"
            )

        template_uuid = str(uuid.uuid4())
        file_path = TEMPLATE_DIR / f"{template_uuid}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(template_json, f, indent=2)

        logger.info(f"Template file saved to disk | path={file_path}")

        db_file = Files(
            file_name=file.filename,
            file_path=str(file_path),
            file_type="json"
        )

        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        logger.info(f"Template file DB record created | file_id={db_file.id}")

        db_template = MarketplaceTemplate(
            template_name=templateName,
            version=version,
            file_id=db_file.id
        )

        db.add(db_template)
        db.commit()
        db.refresh(db_template)

        logger.info(
            f"Marketplace template created | template_id={db_template.id} | marketplace={templateName} | version={version}"
        )

        return {
            "message": "Template uploaded successfully",
            "templateId": db_template.id,
            "fileId": db_file.id,
            "template_name": templateName,
            "version": version
        }

    except Exception:
        logger.exception("Template upload failed")
        raise

    finally:
        db.close()
        logger.debug("Database session closed for uploadTemplate")


def getTemplate(marketplace_name: str):
    logger.info(f"Fetching template | marketplace={marketplace_name}")

    db: Session = SessionLocal()
    try:
        template = (
            db.query(MarketplaceTemplate)
            .filter(MarketplaceTemplate.template_name == marketplace_name)
            .first()
        )

        if not template:
            logger.warning(f"Template not found | marketplace={marketplace_name}")
            return {"message": "Template not found"}

        file = (
            db.query(Files)
            .filter(Files.id == template.file_id)
            .first()
        )

        if not file:
            logger.error(f"Template file DB record missing | template_id={template.id}")
            return {"message": "File not found"}

        if not os.path.exists(file.file_path):
            logger.error(f"Template file missing on disk | path={file.file_path}")
            return {"message": "File missing on disk"}

        with open(file.file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        logger.info(f"Template fetched successfully | marketplace={marketplace_name}")

        return {
            "marketplace": template.template_name,
            "template": content
        }

    finally:
        db.close()
        logger.debug("Database session closed for getTemplate")
