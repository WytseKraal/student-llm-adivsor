import students as s
import courses as c
import random as r
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
        "pk": f"STUDENT#{student_id}",
        "sk": f"RESULT#{course_id}",
        "course_id": course_id,
        "assessments": grades,
        # boto3 cant handle floats
        "final_grade":  Decimal(str(final_grade)),
    }


def create_enrollments():
    enrollments = []
    results = []
    for student in s.student_profile:
        student_courses = r.sample(c.courses, r.randint(1, len(c.courses)))
        for course in student_courses:
            enrollment = {
                "pk": f"STUDENT#{student['student_id']}",
                "sk": f"ENROLLMENT#{course['course_id']}",
                "course_id": course['course_id']
            }
            if (course["startdate"]) == "2025-03-15":
                enrollment["status"] = "upcoming"
            elif (course["startdate"]) == "2025-01-15":
                enrollment["status"] = "active"
            else:
                result = create_result_item(
                    student["student_id"],
                    course['course_id'],
                    course['assessment']
                )
                if (result["final_grade"] >= 5.5):
                    enrollment["status"] = "passed"
                else:
                    enrollment["status"] = "failed"
                results.append(result)
            enrollments.append(enrollment)
    return (enrollments, results)
