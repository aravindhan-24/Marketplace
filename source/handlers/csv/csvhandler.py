from fastapi import UploadFile, File, HTTPException
import csv
import io
from typing import List, Dict
from source.constants import SAMPLE_ROW_COUNT, ENCODING
from pydantic import ValidationError
from source.model.fileupload import response

def normalize_row(row: dict, template_fields: list[str]) -> dict:
    normalized = {}

    for field in template_fields:
        value = row.get(field, "")
        normalized[field] = value.strip() if value else ""

    return normalized

def uploadfile(file: UploadFile = File(...)):
    stream = io.TextIOWrapper(file.file, encoding = ENCODING)
    reader = csv.DictReader(stream)
    rowCount = 0
    discoveredHeaders = reader.fieldnames

    sampleRows: List[Dict[str,str]] = []
    for row in reader:
        # Need to pass template here from DB
        #normalized_row = normalize_row(row, )
        rowCount+=1
        if len(sampleRows) < SAMPLE_ROW_COUNT:
            sampleRows.append(row)
            #sampleRows.append(normalized_row)
    return response.FileUploadResponse(header=discoveredHeaders, rowCount=rowCount,SampleRow=sampleRows)