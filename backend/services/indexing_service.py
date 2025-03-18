import re
import boto3
from boto3.dynamodb.conditions import Key
import json
import logging
import os
from backend.models.response import LambdaResponse
from services.base_service import BaseService, APIError
from openai import OpenAI
from pinecone import Pinecone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set up API keys from/and environment variables
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = os.environ.get("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AWS_ENVIRONMENT = os.environ.get("AWS_ENVIRONMENT", "prod")
AWS_REGION = os.environ.get("AWS_REGION", "eu-north-1")
DYNAMODB_TABLE_NAME = f"{AWS_ENVIRONMENT}-student-advisor-table"


class EmbeddingService(BaseService):
    def __init__(self, event, context):
        super().__init__(event, context)

        logger.info(f"Received event: {json.dumps(self.event.model_dump())}")

        if not all([PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX_NAME]):
            logger.error(
                "Missing one or more required Pinecone environment variables.")
            raise APIError(
                "Missing one or more required Pinecone environment variables.",
                status_code=500)

        if not OPENAI_API_KEY:
            logger.error("Missing OpenAI API key")
            raise APIError("Missing OpenAI API key", status_code=500)

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.pinecone = Pinecone(
            api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        self.index = self.pinecone.Index(PINECONE_INDEX_NAME)
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        self.table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    def handle(self) -> dict:
        http_method = self.event.httpMethod.upper()
        path = self.event.path

        logger.info("Handling request: %s %s", http_method, path)

        if http_method == "POST" and path == "/":
            # Index all courses
            return self.index_all_courses()

        elif http_method == "POST" and path.startswith("/"):
            # Index a specific course
            course_id = path.lstrip("/")
            if course_id:
                return self.index_course(course_id)

        elif http_method == "DELETE" and path.startswith("/"):
            # Delete a specific course
            course_id = path.lstrip("/")
            if course_id:
                return self.delete_course(course_id)

        elif http_method == "GET" and path == "/health-check":
            # Health check
            return self.health_check()

        else:
            logger.error("Method not allowed")
            raise APIError("Method not allowed", status_code=405)

    def index_all_courses(self):
        """
        Index all courses in the database.
        """
        logger.info("Indexing all courses in Pinecone")
        courses = self.get_all_course_details_with_schedule()

        for course in courses:
            self.index_course(course)

        logger.info(f"Indexed {len(courses)} courses in Pinecone.")

        response = LambdaResponse(
            statusCode=200,
            headers=self.build_headers(),
            body=json.dumps(
                {"message": "Indexed {len(courses)} courses in Pinecone."})
        )
        return response.model_dump()

    def index_course(self, course_id):
        """Index a single course in Pinecone, splitting it by attributes."""
        course = json.loads(self.event.body)
        if course_id not in course:
            logger.error("Missing course ID in request body")
            raise APIError("Missing course ID in request body",
                           status_code=400)

        logger.info(f"Indexing course {course_id} in Pinecone")

        sections = {
            "general": {
                "name": course.get("NAME"),
                "desc": course.get("DESCRIPTION"),
                "start": course.get("STARTDATE"),
                "register": course.get("REGISTRATION_INFO"),
                "remarks": course.get("REMARKS")
            },
            "content_obj_methods": {
                "content": course.get("CONTENTS"),
                "objectives": course.get("OBJECTIVES"),
                "methods": course.get("TEACHING_METHODS")
            },
            "assessment_prereq_studymat": {
                "assessment": course.get("ASSESSMENT"),
                "prerequisites": course.get("PREREQUISITES"),
                "materials": course.get("STUDY_MATERIALS")
            },
            "schedule": course.get("SCHEDULE")
        }

        vectors = []
        for section, content in sections.items():
            if content:
                chunks = self.split_text(content)
                for i, chunk in enumerate(chunks):
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        vector_id = f"{course_id}_{section}_{i}"
                        metadata = {"course_id": course_id, "section": section,
                                    "text": chunk}
                        vectors.append((vector_id, embedding, metadata))

        if vectors:
            upsert_response = self.index.upsert(vectors=vectors)
            logger.info(
                f"Upserted {len(vectors)} vectors for course {course_id}.")
            return upsert_response
        else:
            logger.info(f"No vectors to upsert for course {course_id}.")

    def delete_course(self, course_id):
        """
        Delete a course from the index.
        """
        if not course_id:
            logger.error("Missing course ID in request")
            raise APIError("Missing course ID in request", status_code=400)

        try:
            self.index.delete(vector_ids=[f"{course_id}_*"])
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
        response = self.client.embeddings. \
            create(input=[text], model="text-embedding-3-small")
        embedding = response.data[0].embedding
        # logger.info(
        #     f"Generated embedding for text: {text} \nEmbedding: {embedding}")
        return embedding

    # TODO: Figure out what the best max_chunk_size is <<====================<<
    def split_text(self, text, max_chunk_size=500):
        """
        Splits text into chunks no larger than max_chunk_size.
        Splitting is done on sentence boundaries.
        """
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

    def get_items_sk_begins_with(self, sk_prefix):
        try:
            response = self.table.query(
                KeyConditionExpression=Key('PK').eq("COURSE") & Key('SK').
                begins_with(sk_prefix)
            )
            items = response.get('Items', [])
            return items
        except Exception as e:
            logger.error(f"Error fetching items for {sk_prefix}: {e}")
        return None

    def get_all_course_details_with_schedule(self):
        """
        Get all course details with schedule DynamoDB.
        """
        logger.info("Getting course details and schedules from DynamoDB")

        courses = self.get_items_sk_begins_with(
            "COURSE", "DETAILS").get("Items", [])
        schedules = self.get_items_sk_begins_with(
            "COURSE", "SCHEDULE").get("Items", [])

        schedule_map = {schedule["PK"].split("#")[1]: schedule["SCHEDULE"]
                        for schedule in schedules}

        for course in courses:
            course_id = course["COURSE_ID"]
            if course_id in schedule_map:
                course["SCHEDULE"] = schedule_map[course_id]

        logger.info(f"Retrieved {len(courses)} courses with schedules.")
        return courses
