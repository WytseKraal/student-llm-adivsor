##############################################
# File: hello_handler.py
# directs lambda events to hello_service
##############################################
from pydantic import ValidationError
import logging
from models.event import LambdaEvent
from models.response import LambdaResponse
from services.base_service import APIError
from services.hello_service import HelloService
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict, context: object) -> dict:
    try:
        event_obj = LambdaEvent(**event)
        service = HelloService(event_obj, context)
        http_method = event_obj.httpMethod.upper()

        if http_method == "OPTIONS":
            response = service.options()
        elif http_method == "GET":
            response = service.get()
        else:
            raise APIError("Method not allowed", status_code=405)
    except APIError as e:
        response = LambdaResponse(
            statusCode=e.status_code,
            headers={},
            body=json.dumps({"error": e.message})
        ).dict()
    except ValidationError as ve:
        response = LambdaResponse(
            statusCode=400,
            headers={},
            body=json.dumps({"error": "Invalid event structure",
                             "details": ve.errors()})
        ).dict()
    except Exception as e:
        logger.exception("Unhandled exception")
        response = LambdaResponse(
            statusCode=500,
            headers={},
            body=json.dumps({"error": "Internal server error"})
        ).dict()

    return response
