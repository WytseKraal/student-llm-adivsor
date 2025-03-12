# usage_service.py
import json
import datetime as dt
from pydantic import BaseModel, ValidationError
from typing import Dict
import boto3
from botocore.exceptions import ClientError


class UsageData(BaseModel):
    user_id: str
    token_usage: Dict[str, int]  # A dictionary representing the token usage
    usage_type: str = "REQUEST"  # Default usage type


class UsageService:

    def handle(self, usage_data: Dict) -> Dict:
        """
        Handles the logic for logging the usage data.
        It validates, formats, and logs the data into DynamoDB.
        """
        # TODO
