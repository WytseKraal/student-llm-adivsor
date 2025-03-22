##############################################
# File: event.py
# classes Lambda-, Hello- and GoodbyeResponse
##############################################
from pydantic import BaseModel


class LambdaResponse(BaseModel):
    statusCode: int
    headers: dict[str, str]
    body: str


class HelloResponse(BaseModel):
    message: str


class GoodbyeResponse(BaseModel):
    message: str