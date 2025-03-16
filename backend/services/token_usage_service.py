import json
import logging
import time
import random
import calendar
from models.response import LambdaResponse
import boto3
from boto3.dynamodb.conditions import Key, Attr
from services.base_service import BaseService, APIError
from datetime import datetime as dt
from datetime import timezone
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

            ta = TokenAllocator()
            total = ta.get_total_amount_of_tokens_used_by_user(student_id)

            total = total + total_tokens_used

            usage = {
                "PK": f"{body['student_id']}",
                "SK": f"REQUEST#{dt.timestamp(dt.now())}",
                "USAGE_TYPE": "REQUEST",
                "TOTAL_USAGE": total_tokens_used,
                "PROMPT_USAGE": prompt_usage,
                "COMPLETION_USAGE": completion_usage,
            }

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
            ta = TokenAllocator()
            remaining = ta.get_total_remaining_tokens(student_id)

            return LambdaResponse(
                statusCode=200,
                headers=self.build_headers(),
                body=json.dumps({"tokens_remaining": 0 if remaining < 0 else remaining}, default=self.serialize)
            ).dict()
        except Exception as e:
            raise APIError(f"could not fetch token usage {e}",
                           status_code=500)

    
    def serialize(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)

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


class TokenAllocator:
    MAX_TOKENS = 1_000_000 # max tokens per month

    def get_total_amount_of_tokens_used(self) -> int:
        ts_now = dt.timestamp(dt.now())
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        first_day = self.get_timestamp_of_first_day()
        table = dynamodb.Table(TABLENAME)
        response = table.query(
            IndexName='GSI_TOKENUSAGE_BY_TIME',
            KeyConditionExpression=Key('SK').between(
                f"REQUEST#{first_day}", f"REQUEST#{ts_now}"
                ) & Key('USAGE_TYPE').eq('REQUEST'),
        )

        r = response.get('Items', [])

        return self.calculate_usage(r)

    def get_timestamp_of_first_day(self) -> int:
        now = dt.now()
        first_day = dt(now.year, now.month, 1, tzinfo=timezone.utc)

        ts = int(first_day.timestamp())

        return ts

    def get_total_amount_of_tokens_used_by_user(self, student_id) -> int:
        ts_yesterday = dt.timestamp(dt.now() - datetime.timedelta(hours=24))
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

        r = response.get('Items', [])

        return self.calculate_usage(r)

    def get_total_days_remaining(self):
        now = dt.now()
        total_days = calendar.monthrange(now.year, now.month)[1]

        days_left = total_days - now.day

        return days_left

    def get_total_number_of_students(self) -> int:
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(TABLENAME)
        response = table.query(
            IndexName="GSI_STUDENTS",
            KeyConditionExpression=Key("OTYPE").eq("STUDENT_PROFILE")
        )
        print(response)
        return 10

    def get_total_remaining_tokens(self, student_id) -> int:
        days_left = self.get_total_days_remaining()
        tokens_left = self.MAX_TOKENS - self.get_total_amount_of_tokens_used()
        tokens_left_adjusted = tokens_left * 0.9 # keep 10%.
        number_of_students = self.get_total_number_of_students()

        daily_tokens = (tokens_left_adjusted / days_left) / number_of_students
        max_per_user = daily_tokens * 2
        used_by_user = self.get_total_amount_of_tokens_used_by_user(student_id)

        return int(max_per_user - used_by_user)

    
    def calculate_usage(self, usage):
        total = 0
        if len(usage) > 0:
            for total_count in usage:
                if 'TOTAL_USAGE' in total_count:
                    total = total + int(total_count['TOTAL_USAGE'])

        return total
