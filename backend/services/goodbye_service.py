##############################################
# File: goodbye_service.py
# Service for handling /bye and /seeya
##############################################
from models.response import GoodbyeResponse, LambdaResponse
from services.base_service import BaseService, APIError
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class GoodbyeService(BaseService):
    def handle(self) -> dict:
        http_method = self.event.httpMethod.upper()
        path = self.event.path
        self.logger.info("Handling request: %s %s", http_method, path)
        if http_method == "OPTIONS":
            return self.options()
        elif http_method == "GET":
            if path.endswith("/bye"):
                return self.bye()
            elif path.endswith("/seeya"):
                return self.seeya()
            else:
                raise APIError("Not Found", status_code=404)
        else:
            raise APIError("Method not allowed", status_code=405)

    def bye(self) -> dict:
        payload = GoodbyeResponse(message="bye")
        response = LambdaResponse(
            statusCode=200,
            headers=self.build_headers(),
            body=payload.json()
        )
        return response.dict()

    def seeya(self) -> dict:
        payload = GoodbyeResponse(message="seeya")
        response = LambdaResponse(
            statusCode=200,
            headers=self.build_headers(),
            body=payload.json()
        )
        return response.dict()