from django.contrib.auth import get_user_model
from ai.models import Job


User = get_user_model()


def create_demo_user():
    user, created = User.objects.get_or_create(
        username="recruiter_demo",
        defaults={
            "email": "recruiter.demo@example.com",
            "first_name": "Recruiter",
            "last_name": "Demo",
            "is_staff": True,
        },
    )

    if created:
        user.set_password("ChangeMe123!")
        user.save()
        print("User created: recruiter_demo / ChangeMe123!")
    else:
        print("User already exists: recruiter_demo")

    return user


def get_employment_type(value):
    field = Job._meta.get_field("employment_type")
    valid_values = {choice[0] for choice in field.choices} if field.choices else set()
    return value if value in valid_values else None


def create_jobs():
    user = create_demo_user()

    jobs = [
        {
            "title": "Senior Backend Engineer",
            "company_name": "NexaCloud Technologies",
            "description": "We are seeking a Senior Backend Engineer to design, build, and maintain scalable backend services powering mission-critical digital products. The ideal candidate has strong experience with API design, distributed systems, database optimization, and cloud-native development. You will collaborate closely with product, frontend, DevOps, and QA teams to deliver reliable, secure, and high-performance platforms.",
            "requirements": "5+ years of backend development experience; strong Python and Django knowledge; solid understanding of REST APIs, PostgreSQL, caching, asynchronous processing, testing, CI/CD, Docker, and cloud platforms such as AWS or Azure; excellent problem-solving and communication skills.",
            "employment_type": get_employment_type("full_time"),
            "location": "Remote / Berlin, Germany",
            "created_by": user,
        },
        {
            "title": "Product Manager",
            "company_name": "Altura Digital",
            "description": "Altura Digital is hiring a Product Manager to lead the roadmap and execution of customer-facing software solutions. You will define product strategy, gather business requirements, prioritize features, and align cross-functional teams around clear outcomes. This role requires strong analytical thinking, stakeholder management, and a passion for delivering measurable customer value.",
            "requirements": "4+ years of product management experience; experience writing PRDs and user stories; strong understanding of Agile delivery; ability to work with design, engineering, and business teams; strong communication and data-driven decision-making skills.",
            "employment_type": get_employment_type("full_time"),
            "location": "Paris, France",
            "created_by": user,
        },
        {
            "title": "Data Analyst",
            "company_name": "Insight Harbor",
            "description": "We are looking for a Data Analyst to transform data into meaningful insights that support strategic decisions across the organization. The successful candidate will build dashboards, analyze trends, validate datasets, and communicate findings to technical and non-technical stakeholders.",
            "requirements": "3+ years of experience in data analysis; strong SQL skills; proficiency with Excel, Power BI or Tableau; experience with Python or R is a plus; strong attention to detail; ability to present insights clearly to stakeholders.",
            "employment_type": get_employment_type("full_time"),
            "location": "London, United Kingdom",
            "created_by": user,
        },
        {
            "title": "DevOps Engineer",
            "company_name": "SkyBridge Systems",
            "description": "SkyBridge Systems is seeking a DevOps Engineer to improve deployment reliability, infrastructure automation, and platform observability. In this role, you will manage CI/CD pipelines, containerized services, cloud infrastructure, and monitoring tools.",
            "requirements": "Strong experience with Linux, Docker, Kubernetes, CI/CD pipelines, infrastructure as code, monitoring tools, and cloud platforms; scripting skills in Bash or Python; understanding of networking and security best practices.",
            "employment_type": get_employment_type("full_time"),
            "location": "Amsterdam, Netherlands",
            "created_by": user,
        },
        {
            "title": "UX/UI Designer",
            "company_name": "Lumen Products",
            "description": "We are hiring a UX/UI Designer to craft intuitive, elegant, and accessible digital experiences for web and mobile applications. You will conduct user research, create wireframes and prototypes, define design systems, and collaborate with product and engineering teams.",
            "requirements": "Portfolio demonstrating strong UX and visual design skills; proficiency in Figma or similar design tools; experience with user journeys, wireframing, prototyping, and usability testing; understanding of accessibility and responsive design principles.",
            "employment_type": get_employment_type("full_time"),
            "location": "Barcelona, Spain",
            "created_by": user,
        },
        {
            "title": "Cybersecurity Specialist",
            "company_name": "FortiAxis Security",
            "description": "FortiAxis Security is looking for a Cybersecurity Specialist to help protect internal systems, applications, and data assets from evolving threats. You will support vulnerability assessments, security monitoring, incident response, and policy enforcement.",
            "requirements": "Experience in cybersecurity operations, SIEM tools, vulnerability management, endpoint security, and access control; knowledge of common threat vectors and security frameworks; strong analytical and incident handling skills.",
            "employment_type": get_employment_type("full_time"),
            "location": "Toronto, Canada",
            "created_by": user,
        },
        {
            "title": "Senior Frontend Developer",
            "company_name": "Vertex Flow",
            "description": "Vertex Flow is seeking a Senior Frontend Developer to build responsive, maintainable, and high-performance user interfaces for enterprise applications. You will translate product and design requirements into polished web experiences and contribute to component libraries.",
            "requirements": "Strong proficiency in JavaScript/TypeScript; experience with React, modern frontend tooling, state management, API integration, testing frameworks, and performance optimization; ability to write clean, scalable, and reusable code.",
            "employment_type": get_employment_type("full_time"),
            "location": "Remote",
            "created_by": user,
        },
        {
            "title": "Human Resources Manager",
            "company_name": "Crestline Group",
            "description": "Crestline Group is hiring a Human Resources Manager to lead key HR initiatives across talent acquisition, employee relations, performance management, and policy development. This role requires a people-focused professional who can balance operational excellence with strategic workforce planning.",
            "requirements": "5+ years of HR experience; strong knowledge of recruitment, employee relations, labor practices, and performance processes; excellent interpersonal and conflict-resolution skills; ability to maintain confidentiality and drive organizational effectiveness.",
            "employment_type": get_employment_type("full_time"),
            "location": "Dubai, UAE",
            "created_by": user,
        },
        {
            "title": "Finance Manager",
            "company_name": "Oakridge Capital Advisors",
            "description": "Oakridge Capital Advisors is seeking a Finance Manager to oversee budgeting, financial reporting, forecasting, and internal controls. The successful candidate will provide strategic financial guidance and ensure reporting accuracy.",
            "requirements": "Strong experience in financial analysis, budgeting, reporting, and compliance; proficiency in spreadsheets and financial systems; excellent analytical skills; ability to communicate financial insights to senior stakeholders; CPA/ACCA/CMA is a plus.",
            "employment_type": get_employment_type("full_time"),
            "location": "New York, USA",
            "created_by": user,
        },
        {
            "title": "Customer Success Manager",
            "company_name": "BrightPath SaaS",
            "description": "BrightPath SaaS is looking for a Customer Success Manager to build strong client relationships, drive product adoption, and improve retention across a growing portfolio of accounts. You will serve as a trusted advisor to customers and identify opportunities to expand long-term value.",
            "requirements": "Experience in account management, customer success, or B2B SaaS support; excellent communication and relationship-building skills; strong organizational abilities; comfort working with KPIs, renewals, onboarding, and customer health metrics.",
            "employment_type": get_employment_type("full_time"),
            "location": "Singapore",
            "created_by": user,
        },
    ]

    for job_data in jobs:
        job, created = Job.objects.get_or_create(
            title=job_data["title"],
            company_name=job_data["company_name"],
            defaults=job_data,
        )

        if created:
            print(f"Created job: {job.title}")
        else:
            print(f"Already exists: {job.title}")


create_jobs()