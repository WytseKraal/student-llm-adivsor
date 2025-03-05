import json
import logging
import os
from openai import OpenAI
from models.llm_model import Message, LLMRequest, TokenUsage, LLMResponse
from models.response import LambdaResponse
from services.base_service import BaseService, APIError
from dotenv import load_dotenv
import os



logger = logging.getLogger()
logger.setLevel(logging.INFO)

# load_dotenv()
# logging.info("Loaded environment variables from .env file")


class LLMService(BaseService):
    def __init__(self, event, context):
        super().__init__(event, context)
        event_dict = {
            'httpMethod': event.httpMethod,
            'path': event.path,
            'headers': event.headers,
            'queryStringParameters': event.queryStringParameters,
            'body': event.body if hasattr(event, 'body') else None
        }
        logging.info(f"Received event: {json.dumps(event_dict)}")
    
        api_key = os.getenv('OPENAI_API_KEY')

        logger.info(f"KEY: {api_key}")
        if not api_key:
            logging.error("OPENAI_API_KEY environment variable is not set")
            raise APIError("OpenAI API key not configured", status_code=500)
        
        self.client = OpenAI(api_key=api_key)
        logging.info("Successfully initialized OpenAI client")
        
    def handle(self) -> dict:
        http_method = self.event.httpMethod.upper()
        path = self.event.path
        self.logger.info("Handling request: %s %s", http_method, path)
        
        if http_method == "OPTIONS":
            return self.options()
        elif http_method == "POST":
            return self.generate_completion()
        else:
            raise APIError("Method not allowed", status_code=405)
    
    def generate_completion(self) -> dict:
        try:
            body = json.loads(self.event.body)
            llm_request = LLMRequest(**body)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=llm_request.model,
                messages=[{"role": msg.role, "content": msg.content} for msg in llm_request.messages],
                temperature=llm_request.temperature,
                max_tokens=llm_request.max_tokens
            )
            
            # Extract response data
            content = response.choices[0].message.content
            usage = TokenUsage(
                completion_tokens=response.usage.completion_tokens,
                prompt_tokens=response.usage.prompt_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            llm_response = LLMResponse(
                content=content,
                model=response.model,
                usage=usage,
                id=response.id
            )
            
            # Return formatted response
            response = LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps(llm_response.dict())
            )
            return response.dict()
            
        except json.JSONDecodeError:
            raise APIError("Invalid JSON in request body", status_code=400)
        except Exception as e:
            self.logger.error(f"Error generating completion: {str(e)}")
            raise APIError(f"Error generating completion: {str(e)}", status_code=500)