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


class RAGService(BaseService):
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

        if http_method == "GET":
            return self.get_course_information()
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

    def search_opensearch(self, query_embedding, k=2):
        query = {
            "size": k,
            "query": {"knn": {"embedding": {"vector": query_embedding, "k": k}}},
            "_source": False
        }

        try:
            response = self.opensearch.search(
                index=self.opensearch_index, body=query)
            if "hits" not in response:
                raise APIError(
                    "Failed to retrieve course embeddings", status_code=500)
            return [hit["course_id"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Failed to search OpenSearch: {str(e)}")
            raise APIError(
                f"Failed to search OpenSearch: {str(e)}", status_code=500)

    def fetch_course_information(self, course_ids):
        course_information = []
        for course_id in course_ids:
            response = self.table.get_item(Key={"course_id": course_id})
            if "Item" not in response:
                raise APIError(
                    f"Course {course_id} not found", status_code=404)
            course_information.append(response["Item"])
        return course_information

    def get_course_information(self):
        try:
            body = json.loads(self.event.body)
            query = body.get("query")
            if not query:
                raise APIError("Missing query", status_code=400)

            query_embedding = self.generate_embedding(query)
            relevant_course_ids = self.search_opensearch(query_embedding)
            course_information = self.fetch_course_information(
                relevant_course_ids)
            return {"statusCode": 200, "body": json.dumps(course_information)}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {str(e)}")
            raise APIError(f"Invalid JSON in request body: {str(e)}",
                           status_code=400)
        except Exception as e:
            logger.error(
                f"Unexpected error generating text embedding: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}", status_code=500)
