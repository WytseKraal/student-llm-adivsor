courses = [{
    "pk": "COURSE#DEVOPS",
    "sk": "DETAILS",
    "course_id": "DEVOPS",
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
    "remarks": "Availability of Canvas site"
  },
  {
    "pk": "COURSE#SOFT_EVOL",
    "sk": "DETAILS",
    "course_id": "SOFT_EVOL",
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
      "Advanced programming skills in multiple languages including functional programming.",
      "Experience with large programming projects.",
      "Ideally, knowledge of compiler construction (parsing, ASTs, basic code analysis).",
      "Good English reading and writing skills."
    ],
    "registration": "More details can be found at https://student.uva.nl/en/topics/course-registration",
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
    "remarks": "The course reader and assignments will be made available on Canvas."
},
{
    "pk": "COURSE#COMPILER",
    "sk": "DETAILS",
    "course_id": "COMPILER",
    "name": "Compiler Construction",
    "description": "As implementations of programming languages, compilers are integral parts of any computing system software stack. The general task of compilers to transform structured text from one format to another is ubiquitous in all areas of computing. This course covers all aspects of modern compiler design and implementation, including lexical and syntactical analysis, context/type checking and inference, high-level code transformations/optimizations, and target code generation.",
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
    "remarks": "All study material as well as lectures are provided in English."
  }]
