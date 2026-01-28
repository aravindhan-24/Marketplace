from pydantic import BaseModel
from typing import List, Dict

class FileUploadResponse(BaseModel):
    fileId: int
    uploadUuid: str
    header: List[str]
    rowCount: int
    sampleRows: List[Dict[str, str]]
