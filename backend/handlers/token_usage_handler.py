##############################################
# File: hello_handler.py
# directs lambda events to TokenUsageservice
##############################################
import json
import logging
from pydantic import ValidationError
from models.event import LambdaEvent
from models.response import LambdaResponse
from services.base_service import APIError
from services.token_usage_service import TokenUsageService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict, context: object) -> dict:
    try:
        event_obj = LambdaEvent(**event)
        service = TokenUsageService(event_obj, context)
        return service.handle()
    except APIError as e:
        return LambdaResponse(
            statusCode=e.status_code,
            headers={},
            body=json.dumps({"error": e.message})
        ).dict()
    except ValidationError as ve:
        return LambdaResponse(
            statusCode=400,
            headers={},
            body=json.dumps({"error": "Invalid event structure",
                             "details": ve.errors()})
        ).dict()
    except Exception as e:
        logger.exception("Unhandled exception")
        return LambdaResponse(
            statusCode=500,
            headers={},
            body=json.dumps({"error": "Internal server error"})
        ).dict()
