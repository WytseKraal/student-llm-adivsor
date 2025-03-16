import boto3
import json
import logging
import os
import boto3.session
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

        # OpenAI API Key check and validation
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.error("Missing OpenAI API key")
            raise APIError("Missing OpenAI API key", status_code=500)
        try:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            # Test OpenAI API connectivity by querying available models
            openai.Model.list()
            logger.info("OpenAI API connection is succesful.")
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API connection failed: {str(e)}")
            raise APIError(
                f"OpenAI API connection failed: {str(e)}", status_code=500)

        # DynamoDB setup and connection check
        environment = os.getenv("Environment", "prod")
        region = os.getenv("AWS_REGION", "eu-north-1")
        self.table_name = f"{environment}-student-advisor-table"
        try:
            self.dynamodb = boto3.resource("dynamodb", region_name=region)
            self.table = self.dynamodb.Table(self.table_name)
            self.table.load()  # Will raise an error if the table is not found
            logger.info("DynamoDB connection is successful.")
        except Exception as e:
            logger.error(f"DynamoDB connection failed: {str(e)}")
            raise APIError(
                f"DynamoDB connection failed: {str(e)}", status_code=500)

        # OpenSearch setup and connection check
        self.opensearch_host = os.getenv("OPENSEARCH_HOST")
        self.opensearch_index = "course_embeddings"
        self.opensearch_port = 443
        credentials = boto3.Session().get_credentials()
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
            # Test OpenSearch connectivity by performing a health check
            self.opensearch.ping()
            logger.info("OpenSearch connection is successful.")
        except Exception as e:
            logger.error(f"OpenSearch connection failed: {str(e)}")
            raise APIError(
                f"OpenSearch connection failed: {str(e)}", status_code=500)

    def handle(self):
        http_method = self.event.httpMethod.upper()
        path = self.event.path

        logger.info("Handling request: %s %s", http_method, path)

        if http_method == "POST":
            return self.process_course()
        elif http_method == "GET":
            return self.get_course_embedding()
        else:
            logger.error(f"Method {http_method} not allowed for path: {path}")
            raise APIError(
                f"Method {http_method} not allowed", status_code=405)

    def generate_embedding(self, text):
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embedding = response['data'][0]['embedding']
            logger.info("Generated embedding successfully.")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise APIError(
                f"Failed to generate embedding: {str(e)}", status_code=500)

    def store_embedding(self, course_id, embedding):
        try:
            doc = {"course_id": course_id, "embedding": embedding}
            self.opensearch.index(index=self.opensearch_index, body=doc)
            logger.info(f"Stored embedding for course {course_id}")
        except Exception as e:
            logger.error(
                f"Failed to store embedding for course {course_id}: {str(e)}")
            raise APIError(
                f"Failed to store embedding for course {course_id}: {str(e)}",
                status_code=500)

    def process_course(self):
        try:
            body = json.loads(self.event.body)
            course_id = body.get("course_id")
            course_text = body.get("text")

            if not course_id or not course_text:
                logger.error("Missing course_id or text in the request body.")
                raise APIError("Missing course_id or text", status_code=400)

            embedding = self.generate_embedding(course_text)
            self.store_embedding(course_id, embedding)

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Embedding stored successfully"})
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {str(e)}")
            raise APIError(
                f"Invalid JSON in request body: {str(e)}", status_code=400)
        except APIError as e:
            logger.error(f"APIError: {e.message}")
            return {
                "statusCode": e.status_code,
                "body": json.dumps({"error": e.message})
            }
        except Exception as e:
            logger.error(f"Unexpected error processing course: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}", status_code=500)

    def get_course_embedding(self):
        try:
            course_id = self.event.queryStringParameters.get("course_id")
            if not course_id:
                logger.error("Missing course_id parameter in query string.")
                raise APIError("Missing course_id parameter", status_code=400)

            # Search for the course embedding in OpenSearch
            search_response = self.opensearch.search(
                index=self.opensearch_index,
                body={
                    "query": {
                        "match": {
                            "course_id": course_id
                        }
                    }
                }
            )

            if not search_response['hits']['hits']:
                logger.error(
                    f"Course embedding not found for course_id: {course_id}")
                raise APIError("Course embedding not found", status_code=404)

            embedding = search_response['hits']['hits'][0]['_source']['embedding']

            return {
                "statusCode": 200,
                "body": json.dumps({"course_id": course_id, "embedding": embedding})
            }
        except Exception as e:
            logger.error(f"Failed to retrieve course embedding: {str(e)}")
            raise APIError(
                f"Failed to retrieve embedding: {str(e)}", status_code=500)
