import json

def lambda_handler(event, context):
    # Get the HTTP method from the event
    http_method = event.get('httpMethod', '')
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': 'https://d10tb7qqmyl8u1.cloudfront.net',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    
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