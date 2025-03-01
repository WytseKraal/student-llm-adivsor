# uploads data to dynamo db
import boto3
import courses
import students
import timetable


def upload():
    dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
    # Select the table
    table = dynamodb.Table('application_database')
    for c in timetable.timetable:
        # Insert data
        print(c['pk'])
        response = table.put_item(
            Item = c
        )
        print("Item inserted:", response)
