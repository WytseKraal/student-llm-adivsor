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


class IndexingService(BaseService):
    def __init__(self, event, context):
        """
        Initialize the IndexingService with event and context.
        """
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

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.pinecone = Pinecone(
            api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        self.index = self.pinecone.Index(PINECONE_INDEX_NAME)
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        self.table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    def handle(self) -> dict:
        """
        Handle the incoming request based on the HTTP method and path.
        """
        http_method = self.event.httpMethod.upper()
        path = self.event.path

        logger.info("Handling request: %s %s", http_method, path)

        if http_method == "OPTIONS":
            return self.options()
        elif http_method == "POST" and path == "/indexing":
            return self.index_all_courses()

        elif http_method == "GET" and path == "/indexing/health-check":
            return self.health_check()

        elif http_method == "POST" and path.startswith("/indexing/"):
            course_id = path.removeprefix("/indexing/")
            if course_id:
                return self.index_course(course_id)
            else:
                logger.error("Course ID not provided in URL for indexing.")
                raise APIError("Missing course ID in URL", status_code=400)

        elif http_method == "DELETE" and path.startswith("/indexing/"):
            course_id = path.removeprefix("/indexing/")
            if course_id:
                return self.delete_course(course_id)
            else:
                logger.error("Course ID not provided in URL for deletion.")
                raise APIError("Missing course ID in URL", status_code=400)

        else:
            logger.error("Method not allowed for path: %s", path)
            raise APIError("Method not allowed", status_code=405)

    def index_all_courses(self):
        """
        Index all courses by retrieving course IDs from the database and
        calling index_course for each.
        """
        logger.info("Indexing all courses in Pinecone")

        try:
            course_ids = self.get_all_course_ids()
            for course_id in course_ids:
                self.index_course(course_id)

            logger.info("Indexed %d courses in Pinecone.", len(course_ids))

            response = LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps(
                    {"message": f"Indexed {len(course_ids)} courses in Pinecone."})
            )
            return response.model_dump()
        except Exception as e:
            logger.error(f"Error indexing all courses: {e}")
            raise APIError("Failed to index all courses", status_code=500)

    def index_course(self, course_id):
        """
        Index a single course in Pinecone using the course_id.
        """
        if not course_id:
            logger.error("Missing course ID in request")
            raise APIError("Missing course ID in request", status_code=400)

        try:
            course_details = self.get_course_details(course_id)
            timetable = self.get_timetable(course_id)

            if not course_details:
                logger.error(f"Course details not found for {course_id}")
                raise APIError(
                    f"Course {course_id} not found", status_code=404)

            # Combine course details with timetable
            course_details["SCHEDULE"] = timetable

            logger.info(f"Indexing course {course_id} in Pinecone")

            sections = {
                "general": {
                    "name": course_details.get("NAME"),
                    "description": course_details.get("DESCRIPTION"),
                    "startdate": course_details.get("STARTDATE"),
                    "registration_info": course_details.get("REGISTRATION_INFO"),
                    "remarks": course_details.get("REMARKS")
                },
                "content_obj_methods": {
                    "content": course_details.get("CONTENTS"),
                    "objectives": course_details.get("OBJECTIVES"),
                    "teaching_methods": course_details.get("TEACHING_METHODS")
                },
                "assessment_prereq_studymat": {
                    "assessment": course_details.get("ASSESSMENT"),
                    "prerequisites": course_details.get("PREREQUISITES"),
                    "study_materials": course_details.get("STUDY_MATERIALS")
                },
                "schedule": course_details.get("SCHEDULE")
            }

            vectors = []
            for section, content in sections.items():
                if isinstance(content, dict):
                    for key, value in content.items():
                        if value:
                            chunks = self.split_text(value)
                            for i, chunk in enumerate(chunks):
                                embedding = self.get_openai_embedding(chunk)
                                if embedding:
                                    vector_id = f"{course_id}_{section}_{key}_{i}"
                                    metadata = {"course_id": course_id,
                                                "section": section, "key": key, "text": chunk}
                                    vectors.append(
                                        (vector_id, embedding, metadata))
                elif isinstance(content, str):
                    chunks = self.split_text(content)
                    for i, chunk in enumerate(chunks):
                        embedding = self.get_openai_embedding(chunk)
                        if embedding:
                            vector_id = f"{course_id}_{section}_{i}"
                            metadata = {"course_id": course_id,
                                        "section": section, "text": chunk}
                            vectors.append((vector_id, embedding, metadata))

            if vectors:
                self.index.upsert(vectors=vectors)
                logger.info("Upserted %d vectors for course %s.",
                            len(vectors), course_id)
                return LambdaResponse(
                    statusCode=200,
                    headers=self.build_headers(),
                    body=json.dumps(
                        {"message": f"Upserted {len(vectors)} vectors to " +
                         f"upsert for course {course_id}."})
                ).model_dump()
            else:
                logger.info("No vectors to upsert for course %s.", course_id)
                return LambdaResponse(
                    statusCode=200,
                    headers=self.build_headers(),
                    body=json.dumps(
                        {"message": f"No vectors to upsert for course {course_id}."})
                ).model_dump()
        except Exception as e:
            logger.error(f"Error indexing course {course_id}: {e}")
            raise APIError("Failed to index course", status_code=500)

    def delete_course(self, course_id):
        """
        Delete a single course from the index using the course_id.
        """
        if not course_id:
            logger.error("Missing course ID in request")
            raise APIError("Missing course ID in request", status_code=400)

        try:
            for ids in self.index.list(prefix=course_id):
                self.index.delete(ids=ids)

            logger.info(
                f"Deleted all vectors for course {course_id} from Pinecone.")
            return LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps(
                    {"message": f"Deleted all vectors for course {course_id}."})
            ).model_dump()
        except Exception as e:
            logger.error(f"Error deleting course {course_id}: {e}")
            raise APIError(
                f"Error deleting course {course_id}", status_code=500)

    def health_check(self):
        """
        Health check endpoint to verify service availability.
        """
        logger.info("Performing health check")

        try:
            # Check Pinecone status
            pinecone_healthy = self.pinecone.describe_index(
                PINECONE_INDEX_NAME)["status"]["ready"]

            # Check DynamoDB connectivity
            try:
                response = self.table.scan(Limit=1)
                dynamo_healthy = "Items" in response
            except Exception as e:
                logger.error(f"DynamoDB health check failed: {e}")
                dynamo_healthy = False

            # Check OpenAI connectivity
            try:
                self.get_openai_embedding("test")
                openai_healthy = True
            except Exception as e:
                logger.error(f"OpenAI health check failed: {e}")
                openai_healthy = False

            status = {
                "pinecone": "healthy" if pinecone_healthy else "unhealthy",
                "dynamodb": "healthy" if dynamo_healthy else "unhealthy",
                "openai": "healthy" if openai_healthy else "unhealthy"
            }

            overall_status = all(
                [pinecone_healthy, dynamo_healthy, openai_healthy])

            logger.info(f"Health check result: {status}")

            return LambdaResponse(
                statusCode=200 if overall_status else 500,
                headers=self.build_headers(),
                body=json.dumps({"status": status})
            ).model_dump()

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}", exc_info=True)
            raise APIError("Health check failed", status_code=500)

    def get_openai_embedding(self, text):
        """
        Generate embedding for a given text using
        OpenAI's text-embedding-3-small model.
        """
        try:
            response = self.client.embeddings.create(
                input=[text], model="text-embedding-3-small")
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding request failed: {e}")
            raise APIError("OpenAI embedding generation failed",
                           status_code=500)

    def split_text(self, text, max_chunk_size=500):
        """
        Splits text into chunks no larger than max_chunk_size.
        Splitting is done on sentence boundaries.
        """
        # Ensure the input is a string
        if not isinstance(text, str):
            text = str(text)  # Convert to string if it's not already a string
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
                current_chunk = f"{current_chunk} {sentence}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    def get_all_course_ids(self):
        """
        Get all course IDs from DynamoDB for all programs.
        """
        logger.info("Retrieving all course IDs from DynamoDB")
        course_ids = []

        try:
            for program in PROGRAMMES:
                response = self.table.query(
                    IndexName="GSI_COURSES_PER_PROGRAM",
                    KeyConditionExpression=Key("CTYPE").begins_with("COURSE")
                    & Key("PROGRAM").eq(program)
                )
                courses = response.get("Items", [])

                for course in courses:
                    course_ids.append(course['COURSE_ID'])

            return course_ids
        except Exception as e:
            logger.error(f"Error retrieving course IDs: {e}")
            raise APIError("Failed to retrieve course IDs", status_code=500)

    def get_course_details(self, course_id):
        """
        Get the details of a course from DynamoDB.
        """
        try:
            response = self.table.query(
                KeyConditionExpression=Key("PK").eq(
                    f"COURSE#{course_id}") & Key("SK").eq("DETAILS")
            )
            items = response.get("Items", [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"Error fetching course details for {course_id}: {e}")
            raise APIError("Failed to fetch course details", status_code=500)

    def get_timetable(self, course_id):
        """
        Get the timetable for a course from DynamoDB.
        """
        try:
            response = self.table.query(
                KeyConditionExpression=Key("PK").eq(
                    f"COURSE#{course_id}") & Key("SK").eq("TIMETABLE")
            )
            items = response.get("Items", [])
            return items[0].get("SCHEDULE") if items else None
        except Exception as e:
            logger.error(
                f"Error fetching course schedule for {course_id}: {e}")
            raise APIError("Failed to fetch course schedule", status_code=500)
