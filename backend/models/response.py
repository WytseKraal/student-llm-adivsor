from pydantic import BaseModel, Field, ValidationError


class LambdaResponse(BaseModel):
    statusCode: int
    headers: dict[str, str]
    body: str

class HelloResponse(BaseModel):
    message: str


class GoodbyeResponse(BaseModel):
    message: str