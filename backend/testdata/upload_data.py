# uploads data to dynamo db
import boto3
import courses
import timetable
import datagenerator

BATCHSIZE = 25
REGION = 'eu-north-1'
TABLENAME = 'prod-student-advisor-table'


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
    upload(courses.courses)
    student_profiles = datagenerator.create_student_profiles(10)
    print(student_profiles)
    upload(student_profiles)
    upload(timetable.timetable)
    enrollments, results = datagenerator.create_enrollments(student_profiles)
    upload(enrollments)
    upload(results)
    print("uploaded data")

if __name__ == "__main__":
    print("going to upload")
    main()