import json
import logging
import time
import random
from models.response import LambdaResponse
import boto3
from boto3.dynamodb.conditions import Key, Attr
from services.base_service import BaseService, APIError
from datetime import datetime as dt
from decimal import Decimal

import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BATCHSIZE = 25
REGION = 'eu-north-1'

TABLENAME = 'dev-student-advisor-table'

MAX_TOTAL_TOKENS = 10_000

class TokenUsageService(BaseService):
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

    def handle(self) -> dict:
        http_method = self.event.httpMethod.upper()
        path = self.event.path

        logger.info("Handling request: %s %s", http_method, path)

        if http_method == "POST":
            return self.upload_token_usage()
        elif http_method == "GET":
            return self.get_token_usage()
        else:
            raise APIError("Method not allowed", status_code=405)

    def upload_token_usage(self) -> dict:
        try:
            body = json.loads(self.event.body)
            student_id = body['student_id']
            total_tokens_used = body['total_usage']
            prompt_usage = body['prompt_usage']
            completion_usage = body['completion_usage']
            if 'student_id' not in body or 'total_usage' not in body or \
                    'prompt_usage' not in body or 'completion_usage' not in body:
                raise APIError(
                    "Missing required fields: student_id, total_tokens, prompt_tokens, completion_tokens", status_code=400)

            print('===')
            print(total_tokens_used)

            token_usage_already_made = self.get_requests(student_id)
            total = self.calculate_usage(token_usage_already_made)
            total = total + total_tokens_used

            print(total)
            print(token_usage_already_made)
            print('===')

            if total >= MAX_TOTAL_TOKENS:
                raise APIError(f"Could not make more requests for student: {student_id}", status_code=400)

            usage = {
                "PK": f"{body['student_id']}",
                "SK": f"REQUEST#{dt.timestamp(dt.now())}",
                "USAGE_TYPE": "REQUEST",
                "TOTAL_USAGE": total_tokens_used,
                "PROMPT_USAGE": prompt_usage,
                "COMPLETION_USAGE": completion_usage,
            }

            print(usage)

            try:
                self.upload([usage])
            except Exception as e:
                raise APIError(f"Could not upload usage to database: {str(e)}", status_code=500)

            return LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps(usage)
            ).dict()

        except json.JSONDecodeError:
            raise APIError("Invalid JSON in request body", status_code=400)


    def get_token_usage(self) -> dict:
        query_params = self.event.queryStringParameters or {}
        student_id = query_params.get('student_id')

        if not student_id:
            raise APIError(
                "Missing required query parameters: student_id", status_code=400)

        try:
            token_usage = self.get_requests(student_id)
            total_used = self.calculate_usage(token_usage)

            return LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps({"tokens_remaining": MAX_TOTAL_TOKENS - total_used}, default=self.serialize)
            ).dict()
        except Exception as e:
            raise APIError(f"could not fetch token usage {e}",
                           status_code=500)

    
    def serialize(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)

    def calculate_usage(self, usage):
        total = 0
        if len(usage) > 0:
            for total_count in usage:
                total = total + total_count['TOTAL_USAGE']

        return total

    def get_requests(self, student_id, h=24):
        ts_yesterday = dt.timestamp(dt.now() - datetime.timedelta(hours=h))
        ts_now = dt.timestamp(dt.now())
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(TABLENAME)
        response = table.query(
            IndexName='GSI_TOKENUSAGE_BY_TIME',
            KeyConditionExpression=Key('SK').between(
                f"REQUEST#{ts_yesterday}", f"REQUEST#{ts_now}"
                ) & Key('USAGE_TYPE').eq('REQUEST'),
            FilterExpression=Attr('PK').eq(f'{student_id}')
        )
        return response.get('Items', [])

    def upload(self, items):
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        # Select the table
        table = dynamodb.Table(TABLENAME)
        with table.batch_writer() as batch:
            for i in range(0, len(items), BATCHSIZE):
                batch_items = items[i:i + BATCHSIZE]
                for item in batch_items:
                    print(f"Uploading: {item['PK']}")
                    batch.put_item(Item=item)