import openai
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()


def generate_embedding(text):
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
        return None


if __name__ == "__main__":
    text = "Liesje leerde lotje lopen langs de lange Lindelaan."

    logger.info(f"Testing embedding generation for text: {text}")
    # logger.info(f"OpenAI API Key: {openai.api_key}")

    embedding = generate_embedding(text)
    if embedding:
        logger.info(f"Generated Embedding: {embedding}")
    else:
        logger.error("Embedding generation failed.")
