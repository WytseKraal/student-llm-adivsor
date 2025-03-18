import re
import boto3
from boto3.dynamodb.conditions import Key
import json
import logging
import os
from models.response import LambdaResponse
from services.base_service import BaseService, APIError
from openai import OpenAI
from pinecone import Pinecone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set up API keys from/and environment variables
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")
PINECONE_HOST = os.environ.get("PINECONE_HOST")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AWS_ENVIRONMENT = os.environ.get("AWS_ENVIRONMENT", "prod")
AWS_REGION = os.environ.get("AWS_REGION", "eu-north-1")
DYNAMODB_TABLE_NAME = f"{AWS_ENVIRONMENT}-student-advisor-table"
PROGRAMMES = ["Master Security and Network Engineering",
              "Master Software Engineering"]


class RAGService(BaseService):
    def __init__(self, event, context):
        super().__init__(event, context)

        logger.info(f"Received event: {json.dumps(self.event.model_dump())}")

        if not all([PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME]):
            logger.error(
                "Missing one or more required Pinecone environment variables. "
                f"{PINECONE_ENVIRONMENT}, {PINECONE_INDEX_NAME}")
            raise APIError(
                "Missing one or more required Pinecone environment variables.",
                status_code=500)

        if not OPENAI_API_KEY:
            logger.error("Missing OpenAI API key")
            raise APIError("Missing OpenAI API key", status_code=500)

    def handle(self) -> dict:
        http_method = self.event.httpMethod.upper()
        path = self.event.path

        logger.info("Handling request: %s %s", http_method, path)

        if http_method == "OPTIONS":
            return self.options()
        elif http_method == "POST" and path == "/rag":
            return self.generate_response()
        else:
            raise APIError("Method not allowed", status_code=405)

    def generate_response(self) -> dict:
        return LambdaResponse(
            statusCode=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps({"relevant_data": ["relevant_data"]})
        ).model_dump()
