##############################################
# File: Hello_service.py
# Service for handling /hello requests
##############################################
from services.base_service import BaseService
from models.response import HelloResponse, LambdaResponse
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

class HelloService(BaseService):
    """Service for handling /hello requests."""
    def get(self) -> dict:
        payload = HelloResponse(message="hello")
        response = LambdaResponse(
            statusCode=200,
            headers=self.build_headers(),
            body=payload.json()
        )
        return response.dict()
