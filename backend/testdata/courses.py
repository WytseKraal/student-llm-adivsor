courses = [{
    "PK": "COURSE#5364DCBS6Y",
    "SK": "DETAILS",
    "course_id": "5364DCBS6Y",
    "name": "DevOps and Cloud-based Software",
    "description": "DevOps is a modern software and applications development model that realizes continuous integration (CI), continuous deployment (CD), and continuous improvement of services and applications, deeply based on cloud virtualization, on-demand services deployment, and precision services monitoring currently available on major cloud platforms.",
    "objectives": [
      "Students are familiar with the concept of DevOps and related technologies, their benefits for organizational IT infrastructure and services management.",
      "Students understand organizational aspects of DevOps and its relation to other technologies.",
      "Students will understand how to build cloud-based applications and use cloud automation tools in the DevOps process applied to various software development scenarios.",
      "Students can analyze practical cloud application problems, apply agile and DevOps practices in teamwork, and develop solutions using cloud computing and automation techniques."
    ],
    "contents": [
      "Introduction to DevOps: core concepts, models, Continuous Delivery (CD), Continuous Integration (CI), Continuous Deployment, Agile development, Scrum, Kanban, Lean.",
      "Cloud Computing architecture: service models, virtualization, resource management, monitoring.",
      "DevOps and software engineering on major cloud platforms: AWS, Microsoft Azure. Cloud-powered applications deployment and accounts management.",
      "Cloud automation tools and platforms: Chef, Terraform, Ansible, and DevOps tools from major cloud providers AWS and Azure.",
      "Software delivery lifecycle in an agile DevOps organization, QA in cloud-based software development systems, secure applications development with DevSecOps.",
      "DevOps applications architecture, configuration management, monitoring, environment setup on selected cloud platforms AWS or Microsoft Azure.",
      "Guest lectures from local cloud providers and DevOps companies."
    ],
    "prerequisites": ["Familiarity with Java, C, or Python", "Experience with any IDE platform"],
    "registration_info": "https://student.uva.nl/en/topics/course-registration",
    "teaching_methods": [
      "Lecture",
      "Self-study",
      "Working independently on a project or thesis",
      "Laptop seminar",
      "Presentation/symposium",
      "Supervision/feedback meeting"
    ],
    "study_materials": ["Online materials provided via Canvas"],
    "assessment": [
      "Individual practical assignments",
      "Literature study",
      "Group project report and code",
      "Project development process"
    ],
    "remarks": "Availability of Canvas site",
	"startdate": "2024-05-15" 
  },
  {
    "PK": "COURSE#5364SOEV6Y",
    "SK": "DETAILS",
    "course_id": "5364SOEV6Y",
    "name": "Software Evolution",
    "description": "This course focuses on analyzing large software systems using software quality metrics and empirical techniques.",
    "objectives": [
      "Understand challenges in software development in dynamic teams with changing requirements.",
      "Apply language engineering and empirical software engineering techniques to analyze large codebases.",
      "Analyze scientific contributions addressing software evolution challenges.",
      "Evaluate software analysis tools through experimentation and comparisons."
    ],
    "contents": "The course is designed around lab sessions where students analyze large open-source software systems using Rascal. It includes lectures on software maintenance, guest lectures, and practical assignments on clone detection, maintainability metrics, and automated refactoring.",
    "prerequisites": [
      "Advanced programming ills in multiple languages including functional programming.",
      "Experience with large programming projects.",
      "Ideally, knowledge of compiler construction (parsing, ASTs, basic code analysis).",
      "Good English reading and writing ills."
    ],
    "registration_info": "More details can be found at https://student.uva.nl/en/topics/course-registration",
    "teaching_methods": [
      "Lecture",
      "Laptop seminar",
      "Computer lab session/practical training",
      "Self-study",
      "Presentation/symposium"
    ],
    "study_materials": {
      "syllabus": "Reader consisting of selected papers on software evolution.",
      "other": [
        "http://www.rascal-mpl.org",
        "Potentially other academic sources made available on Canvas."
      ]
    },
    "assessment": [
      "Practical lab assignments performed in pairs, assessed via demonstration/presentation and report.",
      "Individual reading and writing exercise (annotated bibliography for selected papers)."
    ],
    "remarks": "The course reader and assignments will be made available on Canvas.",
	"startdate": "2025-01-15" 
},
{
    "PK": "COURSE#5062COMP6Y",
    "SK": "DETAILS",
    "course_id": "5062COMP6Y",
    "name": "Compiler Construction",
    "description": "As implementations of programming languages, compilers are integral parts of any computing system software stack. The general ta of compilers to transform structured text from one format to another is ubiquitous in all areas of computing. This course covers all aspects of modern compiler design and implementation, including lexical and syntactical analysis, context/type checking and inference, high-level code transformations/optimizations, and target code generation.",
    "objectives": [
      "To develop a profound understanding of the inner workings of compilers.",
      "To develop the ability to design and implement compilers for varying purposes."
    ],
    "contents": [
      "Step-by-step coverage of compiler design: lexical and syntactical analysis, context/type checking and inference, high-level code transformations/optimizations, and target code generation.",
      "Case study: CiviC programming language, exposing imperative programming features found in C, Pascal, or Java.",
      "Project-based learning: students develop a fully-fledged compiler targeting a stack-based virtual machine similar to the Java Virtual Machine.",
      "Guest lectures from renowned compiler experts discussing industrial and commercial aspects of compiler construction."
    ],
    "prerequisites": [
      "General programming skills",
      "Working proficiency in C",
      "User-level knowledge of UNIX-like operating systems",
      "General knowledge in computer science aligned with the first two years of a Bachelor's degree in Informatica"
    ],
    "registration_info": "https://student.uva.nl/en/topics/course-registration",
    "teaching_methods": [
      "Lecture",
      "Computer lab session/practical training",
      "Self-study",
      "Working independently on a project or thesis"
    ],
    "study_materials": [
      "The course does not follow any specific textbook, but recommended readings include:",
      "Compilers: Principles, Techniques, and Tools - Aho, Lam, Sethi, Ullman",
      "Engineering a Compiler - Cooper, Torczon",
      "Modern Compiler Implementation in C - Appel, Ginsburg",
      "Modern Compiler Design - Grune, van Reeuwijk, Bal, Jacobs, Langendoen",
      "Optimizing Compilers for Modern Architectures - Allen, Kennedy",
      "Practical training material: CiviC language specification, lecture slides, toolchain documentation",
      "Software: CiviC reference compiler, assembler, virtual machine, and compiler construction framework"
    ],
    "assessment": [
      "Theoretical assignments or exam(s)",
      "CiviC Compiler Project",
      "CiviC Compiler Report"
    ],
    "remarks": "All study material as well as lectures are provided in English.",
    "startdate": "2024-03-15" 
  },
  {
    "PK": "COURSE#5364MBDC6Y",
    "SK": "DETAILS",
    "course_id": "5364MBDC6Y",
    "name": "Model-based Design of Cyber-physical Systems",
    "description": "Cyber-physical systems (CPS) integrate computation, sensing, actuation, and networking to interact with and control the physical world. This course focuses on the complexities of CPS and their model-based design methodologies to increase system quality and efficiency.",
    "objectives": [
      "Explain key characteristics and complexity drivers of cyber-physical systems.",
      "Model software behavior using Statecharts and generate code.",
      "Functionally verify systems using methods based on Petri Net models.",
      "Create a domain-specific language (DSL) for model specification and validation.",
      "Verify schedulability of periodic tasks and perform cache analysis on single-core and multi-core systems.",
      "Explain design-space exploration for optimizing cost, performance, and energy consumption.",
      "Collaborate in teams to develop model-based software for cyber-physical systems."
    ],
    "contents": [
      "Introduction to cyber-physical systems and their complexity drivers.",
      "Model-based specification, analysis, and verification of CPS behavior.",
      "Software development for CPS using model-based methodologies.",
      "Hardware and software configurations for optimized CPS performance."
    ],
    "prerequisites": ["Programming experience in Java, Python, or C++", "Computer Organization (preferred, not mandatory)"],
    "registration_info": "https://student.uva.nl/en/topics/course-registration",
    "teaching_methods": [
      "Lecture",
      "Laptop seminar",
      "Self-study",
      "Working independently on a project or thesis"
    ],
    "assessment": [
      "Three assignments",
      "Practical group project"
    ],
    "remarks": "A Canvas site for the course is available.",
    "startdate": "2025-03-15"
  },
  {
    "PK": "COURSE#5364SSVT6Y",
    "SK": "DETAILS",
    "course_id": "5364SSVT6Y",
    "name": "Software Verification, Validation, and Testing (SVVT)",
    "description": "Software specification, verification, and testing entail checking whether a given software system satisfies given requirements and/or specifications. This course covers formal specifications, type-specification, abstraction, and automated testing methods with a focus on functional and imperative programming in Haskell.",
    "objectives": [
      "Understand and write specifications in the language of predicate logic.",
      "Use type-specification and abstraction to make programs more easily testable.",
      "Write formal specifications for testing Haskell code.",
      "Use random test generation for automating the test process."
    ],
    "contents": [
      "Formal specifications: preconditions and postconditions in software testing.",
      "Random test generation and automated test processes.",
      "Testing functional and imperative programming styles in Haskell."
    ],
    "prerequisites": ["Basic familiarity with logic and functional programming in Haskell"],
    "registration_info": "https://student.uva.nl/en/topics/course-registration",
    "teaching_methods": [
      "Lecture",
      "Seminar",
      "Laptop seminar",
      "Self-study"
    ],
    "study_materials": [
      "Graham Hutton, Programming in Haskell, Cambridge University Press 2016 (Second Edition)",
      "Recommended background reading: Logic in Action (available online)",
      "The Haskell Road to Logic, Maths, and Programming"
    ],
    "assessment": [
      "Course examination with assignments and a final assessment of theoretical and practical components."
    ],
    "remarks": "Course materials and announcements will be provided via Canvas.",
	"startdate": "2025-03-15" 
  }]