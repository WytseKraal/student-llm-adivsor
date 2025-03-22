from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment="Database Schema")

# Define tables and their fields
dot.node("Course_Details", """Course_Details
----------------------
PK (COURSE#ID) [PK]
SK (DETAILS)
""")


dot.node("Course_Timetable", """Course_Timetable
----------------------
PK (COURSE#ID) [PK]
SK (TIMETABLE)
""")


dot.node("GSI_COURSES_PER_PROGRAM", """GSI_COURSES_PER_PROGRAM
----------------------
PK (PROGRAM) [GSI]
SK (CTYPE)""")




dot.edge("Course_Details", "Course_Timetable", label="Scheduled as")
dot.edge("Course_Details", "GSI_COURSES_PER_PROGRAM", label="Indexed by")

# Render the diagram
dot.render("database_schema_public", format="png")