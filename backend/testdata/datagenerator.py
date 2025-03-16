import courses as c
import random as r
import names
from decimal import Decimal


# Generate a dictionary of random grades for assessments.
def generate_random_grades(asss):
    grades = {
        assessment: Decimal(str(
            round(r.uniform(1.0, 10.0), 1)
         )) for assessment in asss
        }
    final_grade = round(sum(grades.values()) / len(grades), 1)
    return grades, final_grade


# Create a result item for a student.
def create_result_item(student_id, course_id, asss):
    grades, final_grade = generate_random_grades(asss)
    return {
        "PK": f"STUDENT#{student_id}",
        "SK": f"RESULT#{course_id}",
        "COURSE_ID": course_id,
        "ASSESSMENTS": grades,
        # boto3 cant handle floats
        "FINAL_GRADE":  Decimal(str(final_grade)),
    }


def create_enrollments(students):
    enrollments = []
    results = []
    for student in students:
        student_courses = r.sample(c.courses, r.randint(1, len(c.courses)))
        for course in student_courses:
            enrollment = {
                "PK": f"STUDENT#{student['STUDENT_ID']}",
                "SK": f"ENROLLMENT#{course['COURSE_ID']}",
                "COURSE_ID": course['COURSE_ID']
            }
            if (course["STARTDATE"]) == "2025-03-15":
                enrollment["STATUS"] = "upcoming"
            elif (course["STARTDATE"]) == "2025-01-15":
                enrollment["STATUS"] = "active"
            else:
                result = create_result_item(
                    student["STUDENT_ID"],
                    course['COURSE_ID'],
                    course['ASSESSMENT']
                )
                if (result["FINAL_GRADE"] >= 5.5):
                    enrollment["STATUS"] = "passed"
                else:
                    enrollment["STATUS"] = "failed"
                results.append(result)
            enrollments.append(enrollment)
    return (enrollments, results)


def create_student_profiles(amount=10):
    students = []
    for i in range(0, amount):
        student_id = r.randint(10000, 99999)
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        student = {
            "PK": f"STUDENT#{student_id}",
            "SK": "PROFILE",
            "STUDENT_ID": student_id,
            "FIRST_NAME": first_name,
            "PREFERRED_NAME": first_name,
            "LAST_NAME": last_name,
            "EMAIL": f"{first_name}.{last_name}@uva.nl",
            "PROGRAM": "Master Software Engineering",
            "YEAR": 1
        }
        students.append(student)
    return students
