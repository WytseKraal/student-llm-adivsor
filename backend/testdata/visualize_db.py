from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment="Database Schema")

# Define tables and their fields
dot.node("Course_Details", """Course_Details
----------------------
PK (COURSE#ID) [PK]
SK (DETAILS)
COURSE_ID
NAME
DESCRIPTION
OBJECTIVES (List)
CONTENTS (List)
PREREQUISITES (List)
TEACHING_METHODS (List)
ASSESSMENT (List)
STUDY_MATERIALS
STARTDATE
REGISTRATION_INFO""")

dot.node("Student_Profile", """Student_Profile
----------------------
PK (STUDENT#ID) [PK]
SK (PROFILE)
STUDENT_ID
FIRST_NAME
LAST_NAME
EMAIL
PROGRAM
YEAR""")

dot.node("Student_Enrollment", """Student_Enrollment
----------------------
PK (STUDENT#ID) [PK]
SK (ENROLLMENT#COURSE_ID)
COURSE_ID
STATUS""")

dot.node("Student_Result", """Student_Result
----------------------
PK (STUDENT#ID) [PK]
SK (RESULT#COURSE_ID)
COURSE_ID
ASSESSMENTS (List)
FINAL_GRADE""")

dot.node("Course_Timetable", """Course_Timetable
----------------------
PK (COURSE#ID) [PK]
SK (TIMETABLE)
SCHEDULE (Nested Dict)""")

# Define relationships
dot.edge("Student_Profile", "Student_Enrollment", label="Enrolls in")
dot.edge("Student_Profile", "Student_Result", label="Has results in")
dot.edge("Course_Details", "Student_Enrollment", label="Enrollment for")
dot.edge("Course_Details", "Student_Result", label="Assessment for")
dot.edge("Course_Details", "Course_Timetable", label="Scheduled as")

# Render the diagram
dot.render("database_schema", format="png")