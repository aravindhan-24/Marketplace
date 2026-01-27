from fastapi import APIRouter, Depends, HTTPException, Query 
from sqlalchemy.orm import Session
from source.model.mapper.mapping_request import MappingRequest 
from source.db.model import SellerMapping
from source.db.session import SessionLocal

def mapper(payload: MappingRequest):
    db: Session = SessionLocal()
    try:
        new_mapping = SellerMapping(
            seller=payload.seller,       
            marketplace=payload.marketplace,
            column_mapping=payload.mapping
        )

        db.add(new_mapping)
        db.commit()
        
        db.refresh(new_mapping)

        return {
            "status": "success",
            "message": "Mapping persisted",
            "id": new_mapping.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
def get_mapping(id: str):
    db: Session = SessionLocal()
    try:
        mapping_record = db.query(SellerMapping).filter(
            SellerMapping.id == id
        ).first()

        if not mapping_record:
            raise HTTPException(
                status_code=404, 
                detail=f"Mapping for seller '{id}' not found"
            )

        return {
            "status": "success",
            "data": {
                "id": mapping_record.id,
                "seller": mapping_record.upload_id,
                "marketplace": mapping_record.marketplace,
                "mapping": mapping_record.column_mapping,
                "created_at": mapping_record.created_at
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

def get_mapping_by_id(mapping_id: int):
    db: Session = SessionLocal()
    try:
        mapping_record = db.query(SellerMapping).get(mapping_id)

        if not mapping_record:
            raise HTTPException(status_code=404, detail="Mapping not found")

        return {
            "status": "success",
            "data": {
                "id": mapping_record.id,
                "seller": mapping_record.seller,
                "marketplace": mapping_record.marketplace,
                "mapping": mapping_record.column_mapping,
                "created_at": mapping_record.created_at
            }
        }
    finally:
        db.close()
