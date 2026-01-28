from fastapi import UploadFile, File, HTTPException, Depends, Query
import csv,uuid
from source.constants import SAMPLE_ROW_COUNT, ENCODING
from pathlib import Path
from sqlalchemy.orm import Session
from source.db.session import SessionLocal
from source.db.model import Files, SellerCsvUpload
from constants import ENCODING ,SAMPLE_ROW_COUNT, UPLOAD_DIR



def uploadfile(
    seller_id: str = Query(...),
    file: UploadFile = File(...)
):
    db: Session = SessionLocal()
    try:
        if Path(file.filename).suffix.lower() != ".csv":
            raise HTTPException(400, "Only CSV files allowed")

        upload_uuid = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{upload_uuid}.csv"

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        with open(file_path, newline="", encoding=ENCODING) as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            row_count = 0
            sample_rows = []

            for row in reader:
                row_count += 1
                if len(sample_rows) < SAMPLE_ROW_COUNT:
                    sample_rows.append(row)

        db_file = Files(
            file_name=file.filename,
            file_path=str(file_path),
            file_type="csv"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        csv_upload = SellerCsvUpload(
            seller_id=seller_id,
            csv_file_id=db_file.id
        )
        db.add(csv_upload)
        db.commit()
        db.refresh(csv_upload)

        return {
            "csvUploadId": csv_upload.id,
            "fileId": db_file.id,
            "headers": headers,
            "rowCount": row_count,
            "sampleRows": sample_rows
        }
    finally:
        db.close()
