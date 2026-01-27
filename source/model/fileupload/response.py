from pydantic import BaseModel
from typing import List,Dict

class FileUploadResponse(BaseModel):
    header: List[str]
    rowCount: int
    SampleRow: List[Dict[str,str]]