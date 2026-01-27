from fastapi import UploadFile, File, HTTPException
import csv, io,os,uuid
from typing import List, Dict
from source.constants import SAMPLE_ROW_COUNT, ENCODING
from pydantic import ValidationError
from source.model.fileupload import response
from pathlib import Path

UPLOAD_DIR = Path("C:/Users/Jo/Desktop/streamoid/Marketplace/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def uploadfile(file: UploadFile = File(...)):
    
    upload_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{upload_id}.csv")

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    with open(file_path, newline="", encoding=ENCODING) as f:
        reader = csv.DictReader(f)

        discoveredHeaders = reader.fieldnames
        rowCount = 0
        sampleRows: List[Dict[str, str]] = []

        for row in reader:
            rowCount += 1
            if len(sampleRows) < SAMPLE_ROW_COUNT:
                sampleRows.append(row)

    return response.FileUploadResponse(
        uploadId=upload_id,
        header=discoveredHeaders,
        rowCount=rowCount,
        SampleRow=sampleRows
    )