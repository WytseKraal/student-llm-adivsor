import json
import os
import logging



def lambda_handler(event, context):
    http_method = event.get('httpMethod', '')

    # Handle OPTIONS request (CORS preflight)
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'body': ''
        }
    
    # Handle GET request
    if http_method == 'GET':
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'hello'})
        }
    
    # Handle other methods
    return {
        'statusCode': 405,
        'body': json.dumps({'message': 'Method not allowed'})
    }