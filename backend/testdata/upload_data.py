# uploads data to dynamo db
import boto3
import courses
import timetable
import datagenerator

BATCHSIZE = 25
REGION = 'eu-north-1'
TABLENAME = 'application_database'


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
    uuids = ['f05cc95c-4021-70f6-792e-1df97c8f6262', 'f0ece98c-40b1-701f-c788-74aafbe9bd90', '20fcf98c-b0d1-7016-0374-895b4b7a4ead']
    for i in range(len(uuids)):
        student_profiles[i]['STUDENT_ID'] = uuids[i]
        student_profiles[i]['PK'] = f"STUDENT#{uuids[i]}"
    upload(student_profiles)
    print("DOING THE TIMETABLE....")
    upload(timetable.timetable)
    print("FINSIHED DOING TIMETABLE")
    enrollments, results = datagenerator.create_enrollments(student_profiles)
    upload(enrollments)
    upload(results)
    print("uploaded data")

if __name__ == "__main__":
    print("going to upload")
    main()