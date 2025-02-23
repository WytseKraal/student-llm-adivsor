import os
import logging
from pydantic import BaseModel, Field, ValidationError
from models.event import LambdaEvent
from models.response import LambdaResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# TODO: Move APIError
# TODO: Retrieve urls from .env file
# TODO: use model dump and json dump

class APIError(Exception):
    """
    Generic API error handler
    """
    def __init__(self, message: str, status_code: int=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class BaseService:
    """
    Base service for handling and creating lambda services and endpoints
    """
    def __init__(self, event: LambdaEvent, context: object):
        self.event = event
        self.context = context
        self.environment = os.environ.get('Environment', 'dev').lower()
        self.logger = logger
    
    def get_cors_origin(self):
        self.logger.info(f"Current env: {self.environment}")
        return 'http://13.53.152.71' if self.environment == 'prod' else 'http://localhost:3000'
    
    def build_headers(self) -> dict[str, str]:
        request_origin = self.event.headers.get('origin', '')
        cors_origin = self.get_cors_origin()
        allowed_origin = cors_origin if request_origin == cors_origin else ''
        return {
            'Access-Control-Allow-Origin': allowed_origin,
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Origin',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        }

    
    def options(self) -> dict:
        """
        Preflight check
        """
        response = LambdaResponse(statusCode=200, headers=self.build_headers(), body='')
        return response.dict()
        

    def get(self) -> dict:
        """Default GET handler (should be overridden by subclasses if needed)."""
        raise APIError('GET method not implemented', status_code=405)

    def post(self) -> dict:
        """Default POST handler (should be overridden by subclasses if needed)."""
        raise APIError('POST method not implemented', status_code=405)
