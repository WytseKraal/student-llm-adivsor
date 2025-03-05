import openai
import os
import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
from services.base_service import BaseService, APIError
from models.response import LambdaResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = 'eu-north-1'
TABLENAME = 'prod-student-advisor-table'
STUDENT = 'STUDENT#f05cc95c-4021-70f6-792e-1df97c8f6262'

class ChatService(BaseService):
    def __init__(self, event, context):
        super().__init__(event, context)

        # Load OpenAI API key
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise APIError("Missing OpenAI API key", status_code=500)
        
        logger.info(f"APIKEY: {self.openai_api_key}")

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

            enrollments = self.get_items_sk_begins_with(STUDENT, 'ENROLLMENT')
            grades = self.get_items_sk_begins_with(STUDENT, 'RESULT')
            profile = self.get_items_sk_begins_with(STUDENT, 'PROFILE')
            timetable = self.get_items_sk_begins_with(STUDENT, 'TIMETABLE')

            prompt = f"""
            You are an expert student helper.
            The profile of this student is: {profile}

            The grades of this student is: {grades}

            This student is enrolled in: {enrollments}

            This students time table is: {timetable}

            Help this student as best as you can with this message, but don't tell them that their grades are low if they are.

            {user_message}
            """

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract OpenAI response
            ai_response = response.choices[0].message.content
            ai_usage = response.usage
            ai_usage_dict = {
                "prompt_tokens": ai_usage.prompt_tokens,
                "completion_tokens": ai_usage.completion_tokens,
                "total_tokens": ai_usage.total_tokens
            }

            response = LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps(
                    {"response": ai_response, "usage": ai_usage_dict})
            )

            return response.dict()

        except json.JSONDecodeError:
            raise APIError("Invalid JSON in request body", status_code=400)
        except Exception as e:
            self.logger.error(f"Error processing OpenAI request: {str(e)}")
            raise APIError("Internal server error", status_code=500)

    def fetch_student_items(self, pk_value):
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(TABLENAME)
        response = None
        try:
            response = table.query(KeyConditionExpression=Key('PK').eq(pk_value))
        except Exception as e:
            print(f"Error fetching items for {pk_value}: {e}")

        return response


    def get_items_sk_begins_with(self, pk_value, sk_prefix):
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(TABLENAME)
        try:
            response = table.query(
                KeyConditionExpression=Key('PK').eq(pk_value) & Key('SK').begins_with(sk_prefix)
            )
            items = response.get('Items', [])
            return items
        except Exception as e:
            print(f"Error fetching items for {pk_value} with sk prefix {sk_prefix}: {e}")
            return None