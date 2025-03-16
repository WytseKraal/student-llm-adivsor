import random as r
from decimal import Decimal

programs = ["Master Software Engineering"]


# Generate a dictionary of random grades for assessments.
def generate_random_grades(asss):
    grades = {
        assessment:
            Decimal(str(round(r.uniform(1.0, 10.0), 1)))
            for assessment in asss
        }
    final_grade = round(sum(grades.values()) / len(grades), 1)
    return grades, final_grade


# Create a result item for a student.
def create_result_item(student_id, course_id, asss):
    grades, final_grade = generate_random_grades(asss)
    return {
        "PK": student_id,
        "SK": f"RESULT#{course_id}",
        "COURSE_ID": course_id,
        "ASSESSMENTS": grades,
        # boto3 cant handle floats
        "FINAL_GRADE":  Decimal(str(final_grade)),
    }


def create_enrollments(student, courses):
    enrollments = []
    results = []
    student_courses = r.sample(courses, r.randint(1, len(courses)))
    for course in student_courses:
        enrollment = {
            "PK": student["PK"],
            "SK": f"ENROLLMENT#{course["COURSE_ID"]}",
            "COURSE_ID": course["COURSE_ID"]
        }
        if (course["STARTDATE"]) == "2025-03-15":
            enrollment["STATUS"] = "upcoming"
        elif (course["STARTDATE"]) == "2025-01-15":
            enrollment["STATUS"] = "active"
        else:
            result = create_result_item(
                student["PK"],
                course["COURSE_ID"],
                course["ASSESSMENT"]
            )
            if (result["FINAL_GRADE"] >= 5.5):
                enrollment["STATUS"] = "passed"
            else:
                enrollment["STATUS"] = "failed"
            results.append(result)
        enrollments.append(enrollment)
    return (enrollments, results)


def create_student_profile(student_uuid, name, email):
    student_id = r.randint(1000000, 9999999)
    student = {
            "PK": f"STUDENT#{student_uuid}",
            "SK": "PROFILE",
            "STUDENT_ID": student_uuid,
            "STUDENT_UUID": student_uuid,
            "NAME": name,
            "PREFERRED_NAME": name,
            "EMAIL": email,
            "PROGRAM": r.choice(programs),
            "OTYPE": "STUDENT_PROFILE",
            "YEAR": 1
    }
    return student
