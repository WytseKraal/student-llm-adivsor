import json
import logging
import time
import random
from models.response import LambdaResponse
from services.base_service import BaseService, APIError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TokenUsageService(BaseService):
    def __init__(self, event, context):
        super().__init__(event, context)

        event_dict = {
            'httpMethod': event.httpMethod,
            'path': event.path,
            'headers': event.headers,
            'queryStringParameters': event.queryStringParameters,
            'body': event.body if hasattr(event, 'body') else None
        }

        logging.info(f"Received event: {json.dumps(event_dict)}")

    def handle(self) -> dict:
        http_method = self.event.httpMethod.upper()
        path = self.event.path

        logger.info("Handling request: %s %s", http_method, path)

        if http_method == "POST":
            return self.upload_token_usage()
        elif http_method == "GET":
            return self.get_token_usage()
        else:
            raise APIError("Method not allowed", status_code=405)

    def upload_token_usage(self) -> dict:
        try:
            body = json.loads(self.event.body)
            if 'student_id' not in body or 'total_tokens' not in body or \
                    'prompt_tokens' not in body or 'completion_tokens' not in body:
                raise APIError(
                    "Missing required fields: student_id, total_tokens, prompt_tokens, completion_tokens", status_code=400)

            mock_response = {
                "message": "Mock: Token usage data stored successfully",
                "student_id": body["student_id"],
                "timestamp": int(time.time()),
                "total_tokens": body["total_tokens"],
                "prompt_tokens": body["prompt_tokens"],
                "completion_tokens": body["completion_tokens"]
            }

            return LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps(mock_response)
            ).dict()

        except json.JSONDecodeError:
            raise APIError("Invalid JSON in request body", status_code=400)

    def get_token_usage(self) -> dict:
        query_params = self.event.queryStringParameters or {}
        student_id = query_params.get('student_id')
        start_time = query_params.get('start_time')
        end_time = query_params.get('end_time')

        if not student_id or not start_time or not end_time:
            raise APIError(
                "Missing required query parameters: student_id, start_time, end_time", status_code=400)

        try:
            # Convert timestamps to integers
            start_time = int(start_time)
            end_time = int(end_time)

            # Generate fake token usage data
            mock_data = [
                {
                    "student_id": student_id,
                    "timestamp": random.randint(start_time, end_time),
                    "total_tokens": random.randint(500, 2000),
                    "prompt_tokens": random.randint(200, 1000),
                    "completion_tokens": random.randint(200, 1000)
                }
                for _ in range(3)  # Generate 2-5 mock records
            ]

            return LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps({"mock_usage_data": mock_data})
            ).dict()

        except ValueError:
            raise APIError(
                "Invalid timestamp format. Use epoch time.", status_code=400)
        except Exception as e:
            logger.error(f"Mock error retrieving token usage: {str(e)}")
            raise APIError("Mock error retrieving token usage",
                           status_code=500)
