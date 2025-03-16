import boto3
from models.response import LambdaResponse
from services.base_service import BaseService, APIError
from boto3.dynamodb.conditions import Key
import json
import logging
from generators import student_generator
from typing import Dict, Any
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
BATCHSIZE = 25


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
        self.table_name = f"{environment}-student-advisor-table"
        logging.info(f"Using {environment} environment")
        
        # Initialize the dynamodb client
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
        self.table = self.dynamodb.Table(self.table_name)
        
        # Test table connection
        try:
            self.table.table_status
            logging.info("Successfully connected to DynamoDB table")
        except Exception as e:
            logging.error(f"Failed to connect to DynamoDB: {str(e)}")
            raise

    def get_items_sk_begins_with(self, pk_value, sk_prefix):
        try:
            response = self.table.query(
                KeyConditionExpression=Key('PK').eq(pk_value) & Key('SK').
                begins_with(sk_prefix)
            )
            items = response.get('Items', [])
            return items
        except Exception as e:
            print(f"""Error fetching items for {pk_value} with sk prefix
                     {sk_prefix}: {e}""")
        return None

    def upload(self, items):
        with self.table.batch_writer() as batch:
            for i in range(0, len(items), BATCHSIZE):
                batch_items = items[i:i + BATCHSIZE]
                for item in batch_items:
                    batch.put_item(Item=item)

    # Returns the tokens of the previous 24 hours
    def get_courses(self, program):
        response = self.table.query(
            TableName=self.table_name,
            IndexName="GSI_COURSES_PER_PROGRAM",
            KeyConditionExpression=Key("CTYPE").begins_with("COURSE")
                 & Key("PROGRAM").eq(program))
        return response.get("Items", [])

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
            # Get student ID from query parameters
            
            student_uuid = body['id']
            student_name = body.get('name', 'Unknown')
            student_email = body.get('email', 'Unknown')
            print(f"Adding student{body}")
            if not student_uuid:
                raise APIError("Missing student ID in query parameters",
                               status_code=400)

            print(f"Body: {body}")
            student = student_generator.create_student_profile(student_uuid,
                                                               student_name,
                                                               student_email)
            print(student)
            courses = self.get_courses(student["PROGRAM"])
            enrollments, results = student_generator.create_enrollments(
                student, courses)

            # Put the item in DynamoDB
            self.table.put_item(Item=student)
            self.upload(enrollments)
            self.upload(results)
            
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
            raise APIError("Missing student ID in query parameters",
                           status_code=400) 
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

            studentID = body["id"]    
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
                Key={"PK": f"STUDENT#{studentID}", "SK": "PROFILE"},
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