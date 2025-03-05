import boto3
from boto3.dynamodb.conditions import Key

REGION = 'eu-north-1'
TABLENAME = 'application_database'
STUDENT = 'STUDENT#10002'


# Connect to local DynamoDB

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLENAME)


# Fetch all items based on pk
def get_items(pk_value):
    try:
        response = table.query(KeyConditionExpression=Key('pk').eq(pk_value))
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


def main():
    # get all data from student:
    print(get_items(STUDENT))
    # get enrollments
    enrollments = get_items_sk_begins_with(STUDENT, "ENROLLMENT")
    print(enrollments)
    # get all info for enrolled courses
    for e in enrollments:
        print(f"Course: {e['COURSE_ID']}")
        print(get_items(f"COURSE#{e['COURSE_ID']}"))
