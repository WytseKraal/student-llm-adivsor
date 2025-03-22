from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment="Database Schema")
dot.attr(rankdir='TB')  # Set top-to-bottom layout

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


# Define GSIs
dot.node("GSI_TOKENUSAGE_BY_TIME", """GSI_TOKENUSAGE_BY_TIME
----------------------
PK (USAGE_TYPE) [GSI]
SK (TIMESTAMP)""")

dot.node("GSI_COURSES_PER_PROGRAM", """GSI_COURSES_PER_PROGRAM
----------------------
PK (PROGRAM) [GSI]
SK (CTYPE)""")

dot.node("GSI_STUDENTS", """GSI_STUDENTS
----------------------
PK (OTYPE) [GSI]""")


# Define relationships
dot.edge("Student_Profile", "Student_Enrollment", label="Enrolls in")
dot.edge("Student_Profile", "Student_Result", label="Has results in")
dot.edge("Student_Profile", "Student_Query", label="Does requests")
dot.edge("Course_Details", "Student_Enrollment", label="Enrollment for")
dot.edge("Course_Details", "Student_Result", label="Assessment for")
dot.edge("Course_Details", "Course_Timetable", label="Scheduled as")

# Connect GSIs to their relevant tables
dot.edge("Student_Query", "GSI_TOKENUSAGE_BY_TIME", label="Indexed by")
dot.edge("Student_Profile", "GSI_STUDENTS", label="Indexed by")
dot.edge("Course_Details", "GSI_COURSES_PER_PROGRAM", label="Indexed by")

# Render the diagram
dot.render("database_schema", format="png")