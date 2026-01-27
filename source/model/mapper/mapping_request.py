from pydantic import BaseModel
from typing import Dict, Any

class MappingRequest(BaseModel):
    seller: str
    marketplace: str
    mapping: Dict[str, Any]