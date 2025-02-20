import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class APIError(Exception):
    """Custom API error for returning a consistent error response."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class BaseHandler:
    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.environment = os.environ.get('Environment', 'dev').lower()
        self.logger = logger
        self.cors_origin = self.get_cors_origin()

    def get_cors_origin(self):
        """Determine the CORS origin based on the environment."""
        self.logger.info(f"Current environment: {self.environment}")
        if self.environment == 'prod':
            return 'https://d10tb7qqmyl8u1.cloudfront.net'
        return 'http://localhost:3000'

    def build_headers(self):
        """Build CORS headers based on the request's origin."""
        request_origin = self.event.get('headers', {}).get('origin', '')
        allowed_origin = self.cors_origin if request_origin == self.cors_origin else ''
        return {
            'Access-Control-Allow-Origin': allowed_origin,
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Origin',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        }

    def handle(self):
        """Dispatch the request based on HTTP method."""
        http_method = self.event.get('httpMethod', '')
        self.logger.info(f"HTTP Method: {http_method}")
        self.logger.info(f"Request headers: {json.dumps(self.event.get('headers', {}))}")
        self.logger.info(f"Environment: {self.environment}")
        self.logger.info(f"CORS origin: {self.cors_origin}")

        if http_method == 'OPTIONS':
            return self.options()
        elif http_method == 'GET':
            return self.get()
        else:
            raise APIError('Method not allowed', status_code=405)

    def options(self):
        """Handle OPTIONS requests."""
        return {
            'statusCode': 200,
            'headers': self.build_headers(),
            'body': ''
        }

    def get(self):
        """Default GET handler. This can be overridden in a subclass."""
        return {
            'statusCode': 200,
            'headers': self.build_headers(),
            'body': json.dumps({'message': 'hello'})
        }

def lambda_handler(event, context):
    try:
        handler = BaseHandler(event, context)
        response = handler.handle()
    except APIError as e:
        response = {
            'statusCode': e.status_code,
            'headers': {},  # Optionally, you could still add CORS headers here.
            'body': json.dumps({'error': e.message})
        }
    except Exception as e:
        logger.exception("Unhandled exception")
        response = {
            'statusCode': 500,
            'headers': {},
            'body': json.dumps({'error': 'Internal server error'})
        }
    return response
