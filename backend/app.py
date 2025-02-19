import os
import json

def lambda_handler(event, context):
    allowed_origin = os.getenv("ALLOWED_ORIGIN", "*")
    
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": allowed_origin,
            "Content-Type": "application/json"
        },
        "body": json.dumps({"message": "Hello from Lambda!"})
    }