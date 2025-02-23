from pydantic import BaseModel, Field, ValidationError

class LambdaEvent(BaseModel):
    httpMethod: str
    headers: dict[str, str] = Field(default_factory=dict)
    path: str = ""