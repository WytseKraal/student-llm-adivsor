import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    allowed_origin = os.environ.get('ALLOWED_ORIGIN', 'http://localhost:3000')

    logger.info(f"Request headers: {json.dumps(event.get('headers', {}))}")
    logger.info(f"Allowed origin: {allowed_origin}")

    headers = {
        'Access-Control-Allow-Origin': allowed_origin,
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }

    http_method = event.get('httpMethod', '')
    logger.info(f"HTTP Method: {http_method}")
    

    # Handle OPTIONS request (CORS preflight)
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Handle GET request
    if http_method == 'GET':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'hello'})
        }
    
    # Handle other methods
    return {
        'statusCode': 405,
        'headers': headers,
        'body': json.dumps({'message': 'Method not allowed'})
    }