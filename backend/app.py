import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_cors_origin():
    environment = os.environ.get('Environment', 'dev').lower()
    if environment == 'prod':
        return 'https://d10tb7qqmyl8u1.cloudfront.net'
    return 'http://localhost:3000'

def lambda_handler(event, context):
    cors_origin = get_cors_origin()
    logger.info(f"Request headers: {json.dumps(event.get('headers', {}))}")
    logger.info(f"Environment: {os.environ.get('Environment', 'dev')}")
    logger.info(f"CORS origin: {cors_origin}")

    headers = {
        'Access-Control-Allow-Origin': cors_origin,
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }

    http_method = event.get('httpMethod', '')
    logger.info(f"HTTP Method: {http_method}")

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