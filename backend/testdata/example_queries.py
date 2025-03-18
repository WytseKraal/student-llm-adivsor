import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime as dt
import datetime

REGION = 'eu-north-1'
TABLENAME = 'dev-student-advisor-table'
STUDENT = 'STUDENT#f05cc95c-4021-70f6-792e-1df97c8f6262'


# Connect to local DynamoDB

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLENAME)


# Fetch all items based on pk
def get_items(pk_value):
    try:
        response = table.query(KeyConditionExpression=Key('PK').eq(pk_value))
        return response.get('Items', [])
    except Exception as e:
        print(f"Error fetching items for {pk_value}: {e}")
        return None


def get_items_sk_begins_with(pk_value, sk_prefix):
    try:
        response = table.query(
            KeyConditionExpression=Key('PK').eq(pk_value) & Key('SK').begins_with(sk_prefix)
        )
        items = response.get('Items', [])
        return items
    except Exception as e:
        print(f"Error fetching items for {pk_value} with sk prefix {sk_prefix}: {e}")
        return None
 

# Returns the tokens of the previous 24 hours
def get_requests(h=24):
    ts_yesterday = dt.timestamp(dt.now() - datetime.timedelta(hours=h))
    ts_now = dt.timestamp(dt.now())
    response = table.query(
        TableName=TABLENAME,
        IndexName='GSI_TOKENUSAGE_BY_TIME',
        KeyConditionExpression=Key('SK').between(
            f"REQUEST#{ts_yesterday}", f"REQUEST#{ts_now}"
            ) & Key('USAGE_TYPE').eq('REQUEST')
    )
    return response.get('Items', [])

# Returns the tokens of the previous 24 hours
def get_students():
    response = table.query(
        TableName=TABLENAME,
        IndexName='GSI_STUDENTS',
        KeyConditionExpression=Key('SK').between(
            f"REQUEST#{ts_yesterday}", f"REQUEST#{ts_now}"
            ) & Key('USAGE_TYPE').eq('REQUEST')
    )
    return response.get('Items', [])


def students_count():
    response = table.query(
        TableName=TABLENAME,
        IndexName="GSI_STUDENTS",
        KeyConditionExpression=Key('OTYPE').eq("STUDENT_PROFILE"),
        Select='COUNT') # Only return the count of items
    print(response)


def main():
    # get all data from student:
    print(get_items(STUDENT))
    print(get_requests(24))
    # get enrollments
    enrollments = get_items_sk_begins_with(STUDENT, "ENROLLMENT")
    print(enrollments)
    # get all info for enrolled courses
    for e in enrollments:
        print(f"Course: {e['COURSE_ID']}")
        print(get_items(f"COURSE#{e['COURSE_ID']}"))
