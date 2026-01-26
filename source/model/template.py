from pydantic import BaseModel
from typing import Literal, Optional, List, Dict

FieldType = Literal[
    "int",
    "number",
    "string",
    "url",
    "enum",
    "stringArray"
    "urlArray",
]    

class FieldRules(BaseModel):
    
    required: bool
    
    type: FieldType
    
    maxLen: Optional[int]= None
    minLen: Optional[int] = None
    
    unique: Optional[bool] = False
    
    allowed: Optional[List[str]] = None

    minItems: Optional[int] = None
    maxItems: Optional[int] = None

class MarketPlaceTemplate(BaseModel):
    templateName: str
    version: str
    fields: Dict[str, FieldRules]
    


