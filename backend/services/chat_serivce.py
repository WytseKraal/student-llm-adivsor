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
environment = os.getenv('Environment', 'prod')
TABLENAME = f'{environment}-student-advisor-table'
AWS_REGION = os.environ.get("AWS_REGION", "eu-north-1")


class ChatService(BaseService):
    def __init__(self, event, context):
        super().__init__(event, context)

        # Load OpenAI API key
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise APIError("Missing OpenAI API key", status_code=500)

        self.client = openai.OpenAI(api_key=self.openai_api_key)
        self.lambda_client = boto3.client("lambda", region_name=AWS_REGION)

        logger.info(f"Received event: {json.dumps(self.event.model_dump())}")

    def handle(self) -> dict:
        http_method = self.event.httpMethod.upper()
        path = self.event.path

        logger.info(f"Handling request: {http_method} {path}")

        if http_method == "OPTIONS":
            return self.options()
        elif http_method == "POST" and path == "/chat":
            return self.generate_response()
        elif http_method == "GET" and path == "/student/check":
            return self.check_student_exists()
        else:
            raise APIError("Method not allowed", status_code=405)

    def check_student_exists(self) -> dict:
        try:
            # Extract student_id from query parameters
            query_parameters = self.event.queryStringParameters or {}
            student_id = query_parameters.get("student_id")

            if not student_id:
                raise APIError(
                    "Missing 'student_id' in query parameters", status_code=400)

            # Format the student ID with the proper prefix
            formatted_student_id = f"STUDENT#{student_id}"

            # Check if student exists in the database
            dynamodb = boto3.resource('dynamodb', region_name=REGION)
            table = dynamodb.Table(TABLENAME)

            # We only need to check if any item exists with this PK
            # Using a limit of 1 to minimize read capacity usage
            response = table.query(
                KeyConditionExpression=Key('PK').eq(formatted_student_id),
                Limit=1
            )

            # If we got any items back, the student exists
            student_exists = len(response.get('Items', [])) > 0

            return LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps({"exists": student_exists})
            ).model_dump()

        except Exception as e:
            logger.error(f"Error checking student existence: {str(e)}")
            raise APIError(f"Error checking student: {str(e)}",
                           status_code=500)

    def removeStudentId(self, data, studentID):
        replacement = "1"
        if isinstance(data, dict):
            return {key: self.removeStudentId(value, studentID) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.removeStudentId(item, studentID) for item in data]
        elif isinstance(data, str):
            return data.replace(studentID, replacement)
        return data

    def generate_response(self) -> dict:
        try:
            body = json.loads(self.event.body)
            user_message = body.get("message")
            student_id = body.get("studentID")

            if not user_message:
                raise APIError("Missing 'message' in request body",
                               status_code=400)

            if not student_id:
                raise APIError("Missing 'studentID' in request body",
                               status_code=400)

            student = f"STUDENT#{student_id}"

            logger.info("Fetching student profile, enrollments, and grades")
            enrollments = self.get_items_sk_begins_with(student, 'ENROLLMENT')
            grades = self.get_items_sk_begins_with(student, 'RESULT')
            profile = self.get_items_sk_begins_with(student, 'PROFILE')

            logger.info("Fetching student timetable and course details")
            course_ids = self.get_unique_course_ids(enrollments)
            all_timetables = {}
            all_courses = []

            for course_id in course_ids:
                course_key = f"COURSE#{course_id}"
                course_timetable = self.get_items_sk_begins_with(course_key,
                                                                 'TIMETABLE')
                course_details = self.get_items_sk_begins_with(course_key,
                                                               "DETAILS")
                all_timetables[course_id] = course_timetable
                all_courses.append(course_details)

            # Get relevant data from the RAG service
            logger.info("Fetching relevant RAG data")
            rag_data = self.get_rag_data(user_message)

            logger.info(f"Student Profile: {profile}")
            logger.info(f"Enrollments: {enrollments}")
            logger.info(f"Grades: {grades}")
            logger.info(f"Timetables: {all_timetables}")
            logger.info(f"Courses: {all_courses}")
            logger.info(f"RAG data: {rag_data}")

            # OpenAI API request with structured messages
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an AI academic advisor specializing in assisting students "
                        "with course information, academic progress, and general student inquiries. "
                        "Your responses should be clear, concise, and professional. "
                        "Always use the student's preferred name, if available. "
                        "When referring to courses, use the course name instead of the course ID. "
                        "Avoid telling students they are underperforming or failing; instead, "
                        "provide constructive guidance on how they can improve their grades. "
                        "Do not make assumptions about courses for which you do not have data. "
                        "Greet the student once at the beginning of the conversation, but avoid repeating greetings. "
                        "You do not need to sign off at the end of the conversation. "
                        "Remember the content of the entire conversation. "
                        "Use Markdown to enhance readability. "
                        "Structure your responses in a way that is detailed yet easy to read and understand. "
                        "Feel free to ask clarifying questions if necessary."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Student Profile: {profile}\n"
                        f"Grades: {grades}\n"
                        f"Enrollments: {enrollments}\n"
                        f"Timetable: {all_timetables}\n"
                        f"Courses: {all_courses}\n\n"
                        f"Relevant RAG data: {rag_data}\n\n"
                        "Based on the above information, assist the student with their query:\n\n"
                        f"{user_message}"
                    )
                }
            ]

            messages = self.removeStudentId(messages, student_id)

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
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

            return response.model_dump()

        except json.JSONDecodeError:
            raise APIError("Invalid JSON in request body", status_code=400)
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise APIError(" Error generating response", status_code=500)

    def fetch_student_items(self, pk_value):
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(TABLENAME)
        response = None
        try:
            response = table.query(KeyConditionExpression=Key('PK').eq(
                pk_value))
        except Exception as e:
            logger.error(f"Error fetching items for {pk_value}: {e}")
            raise Exception(f"Error fetching items for {pk_value}: {e}")

        return response

    def get_items_sk_begins_with(self, pk_value, sk_prefix):
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(TABLENAME)

        try:
            response = table.query(
                KeyConditionExpression=Key('PK').eq(pk_value) &
                Key('SK').begins_with(sk_prefix)
            )
            items = response.get('Items', [])
            return items
        except Exception as e:
            logger.error(
                f"Error fetching items for {pk_value} with sk prefix {sk_prefix}: {e}")
            raise Exception(
                f"Error fetching items for {pk_value} with sk prefix {sk_prefix}: {e}")

    def get_rag_data(self, user_message):
        try:
            response = self.lambda_client.invoke(
                FunctionName="RAGFunction",
                Payload=json.dumps({
                    "path": "/rag",
                    "httpMethod": "POST",
                    "body": json.dumps({"query": user_message})
                })
            )

            response_payload = json.loads(response['Payload'].read())

            # Ensure that "body" is parsed as JSON
            if "body" in response_payload:
                body = json.loads(response_payload["body"])
            else:
                body = {}

            relevant_data = body.get("relevant_data", [])

            return relevant_data
        except Exception as e:
            logger.error(f"Error fetching RAG data: {str(e)}")
            raise Exception("Error fetching RAG data") from e

    def get_unique_course_ids(self, data):
        # Initialize an empty set to store unique course IDs
        unique_course_ids = set()

        # Iterate through each dictionary in the data
        for item in data:
            # Add the course ID to the set
            unique_course_ids.add(item['COURSE_ID'])

        # Convert the set to a list for easier use
        return list(unique_course_ids)
