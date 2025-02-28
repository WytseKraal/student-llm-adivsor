import openai
import os
import json
import logging
from services.base_service import BaseService, APIError
from models.response import LambdaResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ChatService(BaseService):
    def __init__(self, event, context):
        super().__init__(event, context)

        # Load OpenAI API key
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise APIError("Missing OpenAI API key", status_code=500)

        self.client = openai.OpenAI(api_key=self.openai_api_key)

        logger.info(f"Received event: {json.dumps(self.event.dict())}")

    def handle(self) -> dict:
        http_method = self.event.httpMethod.upper()
        path = self.event.path

        self.logger.info("Handling request: %s %s", http_method, path)

        if http_method == "OPTIONS":
            return self.options()
        elif http_method == "POST":
            return self.generate_response()
        else:
            raise APIError("Method not allowed", status_code=405)

    def generate_response(self) -> dict:
        try:
            body = json.loads(self.event.body)
            user_message = body.get("message")

            if not user_message:
                raise APIError("Missing 'message' in request body",
                               status_code=400)

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_message}]
            )

            # Extract OpenAI response
            ai_response = response.choices[0].message.content

            response = LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps({"response": ai_response})
            )
            return response.dict()

        except json.JSONDecodeError:
            raise APIError("Invalid JSON in request body", status_code=400)
        except Exception as e:
            self.logger.error(f"Error processing OpenAI request: {str(e)}")
            raise APIError("Internal server error", status_code=500)
