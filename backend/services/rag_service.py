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

# Set up Pinecone constants
MINIMUM_SCORE = 0.55
TOP_K = 5


class RAGService(BaseService):
    def __init__(self, event, context):
        """
        Initialize the RAGService with event and context.
        """
        super().__init__(event, context)

        logger.info(f"Received event: {json.dumps(self.event.model_dump())}")

        if not all([PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME]):
            logger.error(
                f"Missing one or more required Pinecone environment variables: "
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

    def handle(self) -> dict:
        """
        Handle the incoming request based on the HTTP method and path.
        """
        http_method = self.event.httpMethod.upper()
        path = self.event.path

        logger.info(f"Handling request: {http_method} {path}")

        if http_method == "OPTIONS":
            return self.options()
        elif http_method == "POST" and path == "/rag":
            return self.generate_response()
        else:
            logger.error(f"Method not allowed for path: {path}")
            raise APIError("Method not allowed", status_code=405)

    def generate_response(self) -> dict:
        """
        Generate a response based on the query provided in the request body.
        """
        try:
            body = json.loads(self.event.body)
            query = body.get("query")
            if not query:
                logger.error("Missing 'query' in request body")
                raise APIError(
                    "Missing 'query' in request body", status_code=400)

            # Generate OpenAI embedding for the query
            embedding = self.get_openai_embedding(query)
            # Retrieve relevant course content chunks from Pinecone
            relevant_data = self.retrieve_relevant_data(embedding)

            return LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps({"relevant_data": relevant_data})
            ).model_dump()
        except json.JSONDecodeError as jde:
            logger.error(f"Invalid JSON in request body: {jde}")
            raise APIError("Invalid JSON in request body", status_code=400)
        except Exception as e:
            logger.exception(f"Error generating response: {e}")
            raise APIError(f"Error generating response: {e}", status_code=500)

    def get_openai_embedding(self, text):
        """
        Generate embedding for a given text using OpenAI's 
        text-embedding-3-small model.
        """
        logger.info("Generating OpenAI embedding")

        try:
            response = self.client.embeddings.create(
                input=[text], model="text-embedding-3-small")
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding request failed: {e}")
            raise APIError("OpenAI embedding generation failed",
                           status_code=500)

    def retrieve_relevant_data(self, embedding):
        """
        Retrieve the most relevant course content chunks from Pinecone.
        """
        logger.info("Retrieving relevant data from Pinecone")
        try:
            result = self.index.query(
                vector=embedding, top_k=TOP_K, include_metadata=True)
            relevant_data = []
            for match in result.get("matches", []):
                if match.get("score", 0) > MINIMUM_SCORE:
                    relevant_data.append(match.get("metadata").get("text"))
            logger.info(f"Retrieved {len(relevant_data)} relevant chunks")
            return relevant_data
        except Exception as e:
            logger.error(f"Error retrieving relevant data: {e}")
            raise APIError(
                f"Error retrieving relevant data: {e}", status_code=500)
