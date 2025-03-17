import boto3
import json
import logging
import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from services.base_service import BaseService, APIError
import openai

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EmbeddingService(BaseService):
    def __init__(self, event, context):
        super().__init__(event, context)

        logging.info(f"Received event: {json.dumps(event)}")

        # OpenAI API Setup
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.error("Missing OpenAI API key")
            raise APIError("Missing OpenAI API key", status_code=500)

        try:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            self.test_openai_connection()
            logger.info("OpenAI API connection is successful.")
        except Exception as e:
            logger.error(f"OpenAI API connection failed: {str(e)}")
            raise APIError(
                f"OpenAI API connection failed: {str(e)}", status_code=500)

        # DynamoDB Setup
        environment = os.getenv("Environment", "prod")
        region = os.getenv("AWS_REGION", "eu-north-1")
        self.table_name = f"{environment}-student-advisor-table"

        try:
            self.dynamodb = boto3.resource("dynamodb", region_name=region)
            self.table = self.dynamodb.Table(self.table_name)
            self.table.load()
            logger.info("DynamoDB connection is successful.")
        except Exception as e:
            logger.error(f"DynamoDB connection failed: {str(e)}")
            raise APIError(
                f"DynamoDB connection failed: {str(e)}", status_code=500)

        # OpenSearch Setup
        self.opensearch_host = os.getenv("OPENSEARCH_HOST")
        self.opensearch_index = "course_embeddings"
        self.opensearch_port = 443
        credentials = boto3.Session().get_credentials()
        if not credentials:
            logger.error("AWS credentials not found")
            raise APIError("AWS credentials not found", status_code=500)
        self.aws_auth = AWS4Auth(credentials.access_key,
                                 credentials.secret_key,
                                 region,
                                 "es",
                                 session_token=credentials.token)

        try:
            self.opensearch = OpenSearch(
                hosts=[{"host": self.opensearch_host,
                        "port": self.opensearch_port}],
                http_auth=self.aws_auth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
            )
            self.test_opensearch_connection()
            logger.info("OpenSearch connection is successful.")
        except Exception as e:
            logger.error(f"OpenSearch connection failed: {str(e)}")
            raise APIError(
                f"OpenSearch connection failed: {str(e)}", status_code=500)

    def test_openai_connection(self):
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input="test"
            )
            if "data" not in response:
                raise APIError("OpenAI connection test failed",
                               status_code=500)
        except Exception as e:
            raise APIError(
                f"OpenAI connection test failed: {str(e)}", status_code=500)

    def test_opensearch_connection(self):
        try:
            response = self.opensearch.search(index=self.opensearch_index,
                                              body={"query": {"match_all": {}}})
            if "hits" not in response:
                raise APIError(
                    "OpenSearch connection test failed", status_code=500)
        except Exception as e:
            raise APIError(
                f"OpenSearch connection test failed: {str(e)}", status_code=500)

    def handle(self):
        http_method = self.event.httpMethod.upper()
        path = self.event.path

        logger.info("Handling request: %s %s", http_method, path)

        if http_method == "POST":
            if path == "/text-embedding":
                return self.generate_text_embedding()
            elif path == "/course-embedding":
                return self.post_course_embedding()
        elif http_method == "GET":
            return self.get_course_embedding()
        else:
            logger.error(f"Method {http_method} not allowed for path: {path}")
            raise APIError(
                f"Method {http_method} not allowed", status_code=405)

    def generate_embedding(self, text):
        if not text:
            raise APIError("Missing text parameter", status_code=400)
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small", input=text)
            return response["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise APIError(
                f"Failed to generate embedding: {str(e)}", status_code=500)

    def generate_text_embedding(self):
        try:
            body = json.loads(self.event.body)
            text = body.get("text")
            if not text:
                raise APIError("Missing text", status_code=400)

            embedding = self.generate_embedding(text)
            return {"statusCode": 200, "body": json.dumps({"embedding": embedding})}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {str(e)}")
            raise APIError(f"Invalid JSON in request body: {str(e)}",
                           status_code=400)
        except Exception as e:
            logger.error(
                f"Unexpected error generating text embedding: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}", status_code=500)

    def post_course_embedding(self):
        try:
            body = json.loads(self.event.body)
            course_id = body.get("course_id")
            course_text = body.get("text")
            if not course_id or not course_text:
                raise APIError("Missing course_id or text", status_code=400)

            embedding = self.generate_embedding(course_text)
            self.store_course_embedding(course_id, embedding)
            logger.info(
                f"Generated and stored embedding for course {course_id}")
            return {"statusCode": 200,
                    "body": json.dumps({"message": "Embedding stored successfully"})}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {str(e)}")
            raise APIError(f"Invalid JSON in request body: {str(e)}",
                           status_code=400)
        except Exception as e:
            logger.error(
                f"Unexpected error storing course embedding: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}", status_code=500)

    def store_course_embedding(self, course_id, embedding):
        try:
            doc = {"course_id": course_id, "embedding": embedding}
            self.opensearch.index(index=self.opensearch_index,
                                  id=course_id, body=doc, refresh="wait_for")
        except Exception as e:
            logger.error(
                f"Failed to store embedding for course {course_id}: {str(e)}")
            raise APIError(f"Failed to store embedding for course {course_id}: {str(e)}",
                           status_code=500)

    def get_course_embedding(self):
        try:
            course_id = self.event.queryStringParameters.get("course_id")
            if not course_id:
                raise APIError("Missing course_id parameter", status_code=400)

            response = self.opensearch.get(
                index=self.opensearch_index, id=course_id, ignore=[404])
            if not response or "_source" not in response:
                raise APIError("Course embedding not found", status_code=404)

            return {"statusCode": 200, "body": json.dumps(response["_source"])}
        except Exception as e:
            logger.error(f"Failed to retrieve embedding: {str(e)}")
            raise APIError(
                f"Failed to retrieve embedding: {str(e)}", status_code=500)
