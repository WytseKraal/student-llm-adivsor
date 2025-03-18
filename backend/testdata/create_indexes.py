''' Script to create global secondary indexes'''
import boto3

REGION = 'eu-north-1'
TABLENAME = 'prod-student-advisor-table'

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
        {"AttributeName": "OTYPE", "AttributeType": "S"},
    ],
    "GlobalSecondaryIndexUpdates": [
        {
            "Create": {
               "IndexName": "GSI_STUDENTS",
               "KeySchema": [
                    {"AttributeName": "OTYPE", "KeyType": "HASH"},
                ],
               "Projection": {
                    "ProjectionType": "ALL"
                }
            }
        }
    ]
}


def create_index(index, name):
    dynamodb = boto3.client('dynamodb')
    try:
        response = dynamodb.update_table(**index)
        print(f"{name} creation initiated:", response)
    except Exception as e:
        print("Error updating table:", e)


def main():
    indexes = [(course_index, "course_per_program")]
              # ,(usage_index, "usage_index")]
    for i in indexes:
        (index, name) = i
        create_index(index, name)
