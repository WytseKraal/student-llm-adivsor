''' Script to create global secondary indexes'''
import boto3

REGION = 'eu-north-1'
TABLENAME = 'dev-student-advisor-table'

usage_index = {
    "TableName": TABLENAME,
    "AttributeDefinitions": [
        {"AttributeName": "USAGE_TYPE", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"}
    ],
    "GlobalSecondaryIndexUpdates": [
        {
            "Create": {
               "IndexName": "GSI_TOKENUSAGE_BY_TIME",
               "KeySchema": [
                    {"AttributeName": "USAGE_TYPE", "KeyType": "HASH"},
                    {"AttributeName": "SK", "KeyType": "RANGE"}
                ],
               "Projection": {
                    "ProjectionType": "ALL"
                }
                
            }
        }
    ]
}

course_index = {
    "TableName": TABLENAME,
    "AttributeDefinitions": [
        {"AttributeName": "PROGRAM", "AttributeType": "S"},
        {"AttributeName": "CTYPE", "AttributeType": "S"}
    ],
    "GlobalSecondaryIndexUpdates": [
        {
            "Create": {
               "IndexName": "GSI_COURSES_PER_PROGRAM",
               "KeySchema": [
                    {"AttributeName": "PROGRAM", "KeyType": "HASH"},
                    {"AttributeName": "CTYPE", "KeyType": "RANGE"}
                ],
               "Projection": {
                    "ProjectionType": "ALL"
                }
            }
        }
    ]
}

students_index = {
    "TableName": TABLENAME,
    "AttributeDefinitions": [
        {"AttributeName": "SK", "AttributeType": "S"},
    ],
    "GlobalSecondaryIndexUpdates": [
        {
            "Create": {
               "IndexName": "GSI_STUDENTS",
               "KeySchema": [
                    {"AttributeName": "SK", "KeyType": "HASH"},
                ],
               "Projection": {
                    "ProjectionType": "ALL"
                }
            }
        }
    ]
}


def main():
    dynamodb = boto3.client('dynamodb')
    try:
        response = dynamodb.update_table(**students_index)
        print("student_index creation initiated:", response)
    except Exception as e:
        print("Error updating table:", e)
