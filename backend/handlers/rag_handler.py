##############################################
# File: hello_handler.py
# directs lambda events to RAG_service
##############################################
import json
import logging
from pydantic import ValidationError
from models.event import LambdaEvent
from models.response import LambdaResponse
from services.base_service import APIError
from services.rag_service import RAGService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict, context: object) -> dict:
    try:
        event_obj = LambdaEvent(**event)
        service = RAGService(event_obj, context)
        return service.handle()
    except APIError as e:
        return LambdaResponse(
            statusCode=e.status_code,
            headers={},
            body=json.dumps({"error": e.message})
        ).model_dump()
    except ValidationError as ve:
        return LambdaResponse(
            statusCode=400,
            headers={},
            body=json.dumps({"error": "Invalid event structure",
                             "details": ve.errors()})
        ).model_dump()
    except Exception as e:
        logger.exception("Unhandled exception")
        return LambdaResponse(
            statusCode=500,
            headers={},
            body=json.dumps({"error": f"Internal server error: {e}"})
        ).model_dump()