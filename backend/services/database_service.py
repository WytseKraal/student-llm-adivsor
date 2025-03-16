import boto3
from models.response import LambdaResponse
from services.base_service import BaseService, APIError
import json
import logging
from typing import Dict, Any
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DatabaseService(BaseService):
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
            logging.info(f"AWS Region: {boto3.Session().region_name}")
            
            environment = os.getenv('Environment', 'prod')
            table_name = f"{environment}-student-advisor-table"
            logging.info(f"Using {environment} environment")
            
            # Initialize the dynamodb client
            self.dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
            self.table = self.dynamodb.Table(table_name)
            
            # Test table connection
            try:
                self.table.table_status
                logging.info("Successfully connected to DynamoDB table")
            except Exception as e:
                logging.error(f"Failed to connect to DynamoDB: {str(e)}")
                raise

    def handle(self) -> dict:
        http_method = self.event.httpMethod.upper()
        path = self.event.path
        
        self.logger.info("Handling request: %s %s", http_method, path)
        
        if http_method == "OPTIONS":
            return self.options()
        elif http_method == "PUT":
            return self.put_student()
        elif http_method == "GET":
            return self.get_student()
        elif http_method == "PATCH":
            return self.update_student()
        else:
            print("not allowed")
            raise APIError("Method not allowed", status_code=405)

    def put_student(self) -> dict:
        try:
            body = json.loads(self.event.body)
            print(body)
            if 'id' not in body:
                raise APIError("Missing student ID", status_code=400)
                
            # Put the item in DynamoDB
            self.table.put_item(Item=body)
            
            response = LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps({"message": "Student created successfully"})
            )
            return response.dict()
            
        except json.JSONDecodeError:
            raise APIError("Invalid JSON in request body", status_code=400)

    def get_student(self) -> dict:
        # Get student ID from query parameters
        query_params = self.event.queryStringParameters or {}
        student_id = query_params.get('id')
        
        if not student_id:
            raise APIError("Missing student ID in query parameters", status_code=400) 
        try:
            # Get the item from DynamoDB
            result = self.table.get_item(
                Key={
                    'PK': f"STUDENT#{student_id}",
                    'SK': "PROFILE"
                }
            )
            
            # Check if item exists
            if 'Item' not in result:
                raise APIError("Student not found", status_code=404)
                
            response = LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps(result['Item'], default=lambda x: str(x))
            )
            print(response.dict())
            return response.dict()
            
        except Exception as e:
            self.logger.error(f"Error retrieving student: {str(e)}")
            raise APIError("Error retrieving student", status_code=500)
    
    def update_student(self) -> dict:
        try:
            body = json.loads(self.event.body)
            print(body)
            if 'id' not in body:
                raise APIError("Missing student ID", status_code=400)
                
            update_expressions = []
            expression_attribute_values = {}

            # Check for fields to update
            if "preferredName" in body:
                update_expressions.append("PREFERRED_NAME = :pn")
                expression_attribute_values[":pn"] = body["preferredName"]

            if "email" in body:
                update_expressions.append("EMAIL = :em")
                expression_attribute_values[":em"] = body["email"]

            if not update_expressions:
                raise APIError("No valid fields to update", status_code=400)

            # Construct update expression
            update_expression = "SET " + ", ".join(update_expressions)

            # Update only provided fields
            self.table.update_item(
                Key={"PK": f"STUDENT#{body["id"]}", "SK": "PROFILE"},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            response = LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps({"message": "Student updated successfully"})
            )
            return response.dict()
            
        except json.JSONDecodeError:
            raise APIError("Invalid JSON in request body", status_code=400)