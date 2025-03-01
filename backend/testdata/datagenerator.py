import students as s
import courses as c
import random as r


def create_enrollments():
    enrollments = []
    grades = []
    for st in s.student_profile:
        courses = c.courses
        # get random number for amount of courses
        amount_courses = r.randint(1, len(courses))
        # get a random sample of a random amount of courses
        student_courses = r.sample(courses, amount_courses)
        for stc in student_courses:
            enrollment = {}
            enrollment["pk"] = st["pk"]
            enrollment["sk"] = "ENROLLMENT#{}".format(stc["course_id"])
            if (stc["startdate"]) == "2025-03-15":
                enrollment["status"] = "upcoming"
            if (stc["startdate"]) == "2025-01-15":
                enrollment["status"] = "active"
            else:
                num_ass = len(stc["assessment"])
                numbers = [
                    round(r.uniform(1.0, 10.0), 1) for _ in range(num_ass)
                    ]
                grade = {}
                grade["pk"] = st["pk"]
                grade["sk"] = "RESULTS#{}".format(stc["course_id"])
                ass = []
                for i in range(0, num_ass):
                    ass.append({stc["assessment"][i]: numbers[i]})
                grade["assesments"] = ass
                grade["final_grade"] = round(sum(numbers)/num_ass, 1)
                grades.append(grade)
                if (grade["final_grade"] >= 5.5):
                    enrollment["status"] = "passed"
                else:
                    enrollment["status"] = "failed"
            enrollments.append(enrollment)
    print(enrollments)
    print(grades)
