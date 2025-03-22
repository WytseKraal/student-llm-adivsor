##############################################
# File: upload_coursedata.py
# uploads the course data to dynamodb
##############################################
import boto3
import courses_se
import courses_sec
import timetable_sec
import timetable_se

BATCHSIZE = 25
REGION = 'eu-north-1'
# TABLENAME = 'prod-student-advisor-table'
TABLENAME = 'dev-student-advisor-table'


def upload(items):
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    # Select the table
    table = dynamodb.Table(TABLENAME)
    with table.batch_writer() as batch:
        for i in range(0, len(items), BATCHSIZE):
            batch_items = items[i:i + BATCHSIZE]
            for item in batch_items:
                print(f"Uploading: {item['PK']}")
                batch.put_item(Item=item)


def main():
    upload(courses_se.courses)
    upload(timetable_se.timetable)
    upload(courses_sec.courses)
    upload(timetable_sec.timetable)
 

if __name__ == "__main__":
    print("going to upload")
    main()
