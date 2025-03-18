from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment="Database Schema")

# Define tables and their fields
dot.node("Course_Details", """Course_Details
----------------------
PK (COURSE#ID) [PK]
SK (DETAILS)
""")

dot.node("Student_Profile", """Student_Profile
----------------------
PK (STUDENT#UUID) [PK]
SK (PROFILE)
""")

dot.node("Student_Enrollment", """Student_Enrollment
----------------------
PK (STUDENT#UUID) [PK]
SK (ENROLLMENT#COURSE_ID)
""")

dot.node("Student_Result", """Student_Result
----------------------
PK (STUDENT#UUID) [PK]
SK (RESULT#COURSE_ID)
""")

dot.node("Course_Timetable", """Course_Timetable
----------------------
PK (COURSE#ID) [PK]
SK (TIMETABLE)
""")

dot.node("Student_Query", """Student_Query
----------------------
PK (STUDENT#UUID) [PK]
SK (REQUEST#TIMESTAMP)
""")

# Define relationships
dot.edge("Student_Profile", "Student_Enrollment", label="Enrolls in")
dot.edge("Student_Profile", "Student_Result", label="Has results in")
dot.edge("Student_Profile", "Student_Query", label="Does requests")
dot.edge("Course_Details", "Student_Enrollment", label="Enrollment for")
dot.edge("Course_Details", "Student_Result", label="Assessment for")
dot.edge("Course_Details", "Course_Timetable", label="Scheduled as")

# Render the diagram
dot.render("database_schema", format="png")