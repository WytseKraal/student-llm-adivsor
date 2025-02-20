import json
from app import BaseHandler, APIError  

class GoodbyeHandler(BaseHandler):
    def handle(self):
        http_method = self.event.get('httpMethod', '')
        if http_method == 'OPTIONS':
            return self.options()
        elif http_method == 'GET':
            path = self.event.get('path', '')
            if path.endswith('/bye'):
                return self.bye()
            elif path.endswith('/seeya'):
                return self.seeya()
            else:
                raise APIError('Not Found', status_code=404)
        else:
            raise APIError('Method not allowed', status_code=405)

    def bye(self):
        return {
            'statusCode': 200,
            'headers': self.build_headers(),
            'body': json.dumps({'message': 'bye'})
        }

    def seeya(self):
        return {
            'statusCode': 200,
            'headers': self.build_headers(),
            'body': json.dumps({'message': 'seeya'})
        }

def lambda_handler(event, context):
    try:
        handler = GoodbyeHandler(event, context)
        response = handler.handle()
    except APIError as e:
        response = {
            'statusCode': e.status_code,
            'headers': {},  # Optionally add CORS headers here as needed.
            'body': json.dumps({'error': e.message})
        }
    except Exception as e:
        # Log the unexpected exception.
        BaseHandler.logger.exception("Unhandled exception")
        response = {
            'statusCode': 500,
            'headers': {},
            'body': json.dumps({'error': 'Internal server error'})
        }
    return response
