from sqlalchemy.orm import Session
from source.db.session import SessionLocal
from source.model.csv.csv_template import MarketPlaceTemplate 
from source.db.model import MarketplaceTemplate

def uploadTemplate(req: MarketPlaceTemplate):
    db: Session = SessionLocal()

    try:
        existing = (
            db.query(MarketplaceTemplate)
            .filter(
                MarketplaceTemplate.marketplace_name == req.templateName
            )
            .first()
        )

        if existing:
            return {
                "message": "Template already exists",
                "marketplace": req.templateName
            }

        new_template = MarketplaceTemplate(
            marketplace_name=req.templateName,
            template=req.model_dump(exclude_none=True)
        )

        db.add(new_template)
        db.commit()
        db.refresh(new_template)

        return {
            "message": "Template uploaded successfully",
            "marketplace": new_template.marketplace_name
        }

    finally:
        db.close()

def getTemplate(marketplace_name: str):
    db: Session = SessionLocal()

    try:
        template = (
            db.query(MarketplaceTemplate)
            .filter(
                MarketplaceTemplate.marketplace_name == marketplace_name
            )
            .first()
        )

        if not template:
            return {"message": "Template not found"}

        return {
            "marketplace": template.marketplace_name,
            "template": template.template
        }

    finally:
        db.close()
