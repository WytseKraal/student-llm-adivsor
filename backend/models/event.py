from typing import Dict, Optional
from pydantic import BaseModel, Field, ValidationError

class LambdaEvent(BaseModel):
    httpMethod: str
    headers: dict[str, str] = Field(default_factory=dict)
    path: str = ""
    queryStringParameters: Optional[Dict[str, str]] = None
    body: Optional[str] = None