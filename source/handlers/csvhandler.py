import logging
import csv
import uuid
from pathlib import Path

from fastapi import UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session

from source.constants.constants import ENCODING, SAMPLE_ROW_COUNT, UPLOAD_DIR
from source.db.session import SessionLocal
from source.db.model import Files, SellerCsvUpload

logger = logging.getLogger(__name__)


def uploadfile(
    seller_id: str = Query(...),
    file: UploadFile = File(...)
):
    logger.info(
        f"CSV upload started | seller_id={seller_id} | filename={file.filename}"
    )

    db: Session = SessionLocal()
    try:
        if Path(file.filename).suffix.lower() != ".csv":
            logger.warning(
                f"Invalid file type uploaded | seller_id={seller_id} | filename={file.filename}"
            )
            raise HTTPException(400, "Only CSV files allowed")

        upload_uuid = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{upload_uuid}.csv"

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        logger.info(f"CSV file saved | path={file_path}")

        with open(file_path, newline="", encoding=ENCODING) as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            row_count = 0
            sample_rows = []

            for row in reader:
                row_count += 1
                if len(sample_rows) < SAMPLE_ROW_COUNT:
                    sample_rows.append(row)

        logger.info(
            f"CSV parsed successfully | rows={row_count} | headers={len(headers)}"
        )

        db_file = Files(
            file_name=file.filename,
            file_path=str(file_path),
            file_type="csv"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        logger.info(f"File record created | file_id={db_file.id}")

        csv_upload = SellerCsvUpload(
            seller_id=seller_id,
            csv_file_id=db_file.id
        )
        db.add(csv_upload)
        db.commit()
        db.refresh(csv_upload)

        logger.info(
            f"Seller CSV upload created | csv_upload_id={csv_upload.id} | seller_id={seller_id}"
        )

        return {
            "csvUploadId": csv_upload.id,
            "fileId": db_file.id,
            "headers": headers,
            "rowCount": row_count,
            "sampleRows": sample_rows
        }

    except Exception:
        logger.exception(
            f"CSV upload failed | seller_id={seller_id} | filename={file.filename}"
        )
        raise

    finally:
        db.close()
        logger.debug("Database session closed for CSV upload")
