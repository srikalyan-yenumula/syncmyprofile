
import difflib

from .logging_utils import get_logger, safe_log_text

logger = get_logger(__name__)
ROLE_PROMPTS = {
    "Software Engineer": """
    **Role Analysis: Software Engineer**
    *   **1. Required Skills:**
        *   **Technical:** Proficiency in at least one major language (Python, Java, C++, JavaScript, Go), Data Structures & Algorithms, System Design, Database Management (SQL/NoSQL), Version Control (Git).
        *   **Soft Skills:** Problem-solving, Communication, Teamwork, Adaptability, Attention to Detail.
    *   **2. Responsibilities:**
        *   Design, develop, test, deploy, and maintain software applications.
        *   Write clean, efficient, and testable code.
        *   Participate in code reviews and contribute to engineering best practices.
        *   Collaborate with cross-functional teams (Product, Design, QA) to define requirements.
        *   Troubleshoot and debug production issues.
    *   **3. Technical Expectations:**
        *   Understanding of Software Development Life Cycle (SDLC).
        *   Familiarity with Agile/Scrum methodologies.
        *   Knowledge of CI/CD pipelines and testing frameworks.
        *   Understanding of distributed systems and scalability concepts (for Senior+).
    *   **4. Seniority Expectations:**
        *   **Junior:** Focus on execution of defined tasks, learning the codebase, fixing bugs, writing unit tests. Needs guidance.
        *   **Mid-Level:** Owns features or small components, designs solutions for defined problems, mentors juniors, participates in design discussions. Independent execution.
        *   **Senior:** Owns complex systems or large features, drives technical decisions, defines architecture, mentors the team, handles cross-team dependencies.
        *   **Staff/Principal:** Sets technical strategy, solves organizational-level technical challenges, drives innovation, influences multiple teams.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Software Development", "Object-Oriented Programming (OOP)", "System Design", "Distributed Systems", "RESTful APIs", "Cloud Computing (AWS/Azure/GCP)".
        *   **Must appear in Projects/Experience:** Specific languages (e.g., "Python", "Java"), frameworks (e.g., "Spring Boot", "Django", "React"), tools (e.g., "Docker", "Kubernetes", "Jenkins").
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Lack of specific technologies, vague descriptions of impact, missing metrics, lack of system design keywords (for Senior+).
        *   **Suggest Improvements:** Quantify impact (e.g., "Improved performance by X%"), specify tech stack for every project, add system design details.
        *   **Rebuild Profile:** Focus on "Problem -> Action -> Result" structure. Highlight engineering excellence and problem-solving.
    """,
    "Frontend Developer": """
    **Role Analysis: Frontend Developer**
    *   **1. Required Skills:**
        *   **Technical:** HTML5, CSS3, JavaScript (ES6+), TypeScript, Modern Frameworks (React, Vue, Angular), State Management (Redux, Context API), Build Tools (Webpack, Vite).
        *   **Soft Skills:** UI/UX Sense, Collaboration with Designers, Attention to Detail, Empathy for Users.
    *   **2. Responsibilities:**
        *   Translate design wireframes into high-quality code.
        *   Optimize components for maximum performance across a vast array of web-capable devices and browsers.
        *   Build reusable code and libraries for future use.
        *   Ensure the technical feasibility of UI/UX designs.
    *   **3. Technical Expectations:**
        *   Deep understanding of the DOM and browser rendering behavior.
        *   Knowledge of web accessibility standards (WCAG).
        *   Experience with responsive and adaptive design.
        *   Familiarity with RESTful APIs and GraphQL integration.
    *   **4. Seniority Expectations:**
        *   **Junior:** Implement UI components based on designs, fix UI bugs, write basic logic.
        *   **Mid-Level:** Manage state complexity, optimize rendering performance, handle API integrations, ensure cross-browser compatibility.
        *   **Senior:** Define frontend architecture, set up design systems, mentor team on best practices, make high-level tech stack decisions.
        *   **Staff:** Drive frontend strategy across products, solve complex platform-level UI challenges.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Frontend Development", "Responsive Web Design", "User Interface (UI)", "User Experience (UX)", "Web Performance Optimization", "Accessibility (a11y)".
        *   **Must appear in Projects/Experience:** "React.js", "TypeScript", "Redux", "CSS Modules/SASS", "Jest/Cypress" (Testing).
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Generic descriptions ("Created a website"), lack of modern framework keywords, missing performance metrics.
        *   **Suggest Improvements:** Mention specific libraries used, highlight performance improvements (e.g., "Reduced load time by 20%"), link to live demos or GitHub.
        *   **Rebuild Profile:** Showcase ability to build polished, performant, and accessible user interfaces.
    """,
    "Backend Developer": """
    **Role Analysis: Backend Developer**
    *   **1. Required Skills:**
        *   **Technical:** Server-side languages (Java, Python, Go, Node.js, C#), Databases (SQL, NoSQL), API Design (REST, GraphQL), Caching (Redis, Memcached), Message Queues (Kafka, RabbitMQ).
        *   **Soft Skills:** Logical Thinking, System-Oriented Mindset, Reliability, Security Awareness.
    *   **2. Responsibilities:**
        *   Develop and maintain server-side logic and databases.
        *   Design and implement APIs for frontend and mobile applications.
        *   Optimize applications for speed and scalability.
        *   Implement security and data protection settings.
    *   **3. Technical Expectations:**
        *   Knowledge of microservices architecture vs. monolithic.
        *   Experience with cloud services (AWS, Azure, GCP).
        *   Understanding of containerization (Docker) and orchestration (Kubernetes).
        *   Database schema design and query optimization.
    *   **4. Seniority Expectations:**
        *   **Junior:** Build API endpoints, write database queries, fix backend bugs.
        *   **Mid-Level:** Design database schemas, optimize queries, implement caching, handle service-to-service communication.
        *   **Senior:** Design distributed systems, ensure high availability and fault tolerance, lead architectural decisions.
        *   **Staff:** Define platform engineering strategy, solve complex scalability and concurrency problems.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Backend Development", "API Design", "Microservices", "Database Management", "Scalability", "Cloud Infrastructure".
        *   **Must appear in Projects/Experience:** "Python/Django/Flask", "Java/Spring Boot", "PostgreSQL/MySQL", "MongoDB", "Docker", "AWS Lambda".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus only on coding without system context, lack of scale metrics (requests per second, data volume).
        *   **Suggest Improvements:** Add metrics on scale and performance, mention specific architectural patterns used, highlight security implementations.
        *   **Rebuild Profile:** Emphasize robustness, scalability, and efficiency of solutions.
    """,
    "Full Stack Developer": """
    **Role Analysis: Full Stack Developer**
    *   **1. Required Skills:**
        *   **Technical:** Proficiency in both Frontend (React, Angular, Vue) and Backend (Node.js, Python, Java) technologies. Database management, API integration, DevOps basics.
        *   **Soft Skills:** Versatility, Holistic View, Rapid Prototyping, Communication.
    *   **2. Responsibilities:**
        *   Work on the entire web stack, from the user interface to the database.
        *   Design and develop end-to-end features.
        *   Ensure cross-platform optimization and responsiveness.
        *   Manage project deployment and infrastructure.
    *   **3. Technical Expectations:**
        *   Ability to switch context between client-side and server-side.
        *   Understanding of the full HTTP request lifecycle.
        *   Experience with deployment platforms (Vercel, Netlify, AWS, Heroku).
    *   **4. Seniority Expectations:**
        *   **Junior:** Work on small features across the stack, bug fixes.
        *   **Mid-Level:** Own full features end-to-end, make decisions on data flow and UI state.
        *   **Senior:** Architect complete applications, choose the right stack for the job, mentor both frontend and backend engineers.
        *   **Staff:** Drive technical strategy for entire product lines, optimize engineering velocity.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Full Stack Development", "MERN/MEAN Stack", "Web Architecture", "End-to-End Development".
        *   **Must appear in Projects/Experience:** "React", "Node.js", "Express", "MongoDB", "SQL", "REST API", "GraphQL".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Imbalance between frontend and backend skills (claiming full stack but only showing one), lack of integration details.
        *   **Suggest Improvements:** Demonstrate expertise in both areas, describe the full flow of data in projects.
        *   **Rebuild Profile:** Position as a versatile engineer capable of delivering complete solutions.
    """,
    "Data Scientist": """
    **Role Analysis: Data Scientist**
    *   **1. Required Skills:**
        *   **Technical:** Python/R, SQL, Machine Learning Libraries (Scikit-learn, TensorFlow, PyTorch), Data Visualization (Matplotlib, Seaborn, Tableau), Statistics, Big Data Tools (Spark, Hadoop).
        *   **Soft Skills:** Curiosity, Storytelling with Data, Business Acumen, Critical Thinking.
    *   **2. Responsibilities:**
        *   Analyze large, complex datasets to extract actionable insights.
        *   Build and deploy predictive models and machine learning algorithms.
        *   Design and run A/B tests.
        *   Communicate findings to stakeholders through visualization and reports.
    *   **3. Technical Expectations:**
        *   Strong grasp of statistical concepts and probability.
        *   Experience with data cleaning and feature engineering.
        *   Understanding of model evaluation metrics (Precision, Recall, F1-Score, RMSE).
    *   **4. Seniority Expectations:**
        *   **Junior:** Data cleaning, exploratory analysis, building simple models.
        *   **Mid-Level:** End-to-end modeling pipelines, feature selection, tuning models, deploying to production.
        *   **Senior:** Design complex ML systems, define data strategy, mentor juniors, drive business impact through AI.
        *   **Staff:** Lead AI research initiatives, solve novel problems, influence company-wide data culture.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Data Science", "Machine Learning", "Statistical Analysis", "Predictive Modeling", "Data Visualization", "Deep Learning".
        *   **Must appear in Projects/Experience:** "Python", "Pandas", "NumPy", "SQL", "Jupyter", "A/B Testing".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Listing courses instead of projects, lack of business context (why the model mattered), missing results.
        *   **Suggest Improvements:** Focus on the "So What?", quantify business impact (revenue generated, costs saved), mention specific algorithms used.
        *   **Rebuild Profile:** Highlight the ability to turn data into business value.
    """,
    "Product Manager": """
    **Role Analysis: Product Manager**
    *   **1. Required Skills:**
        *   **Technical:** Understanding of SDLC, Data Analysis (SQL, Excel), A/B Testing, API basics.
        *   **Soft Skills:** Leadership, Empathy, Communication, Prioritization, Stakeholder Management, Strategic Thinking.
    *   **2. Responsibilities:**
        *   Define product vision, strategy, and roadmap.
        *   Gather and analyze user requirements and feedback.
        *   Collaborate with engineering, design, and marketing teams to deliver products.
        *   Prioritize features and manage the product backlog.
    *   **3. Technical Expectations:**
        *   Ability to speak the language of engineers.
        *   Data-driven decision making using analytics tools (Mixpanel, Google Analytics).
        *   Familiarity with Agile/Scrum frameworks.
    *   **4. Seniority Expectations:**
        *   **Junior:** Manage small features, write user stories, coordinate release activities.
        *   **Mid-Level:** Own a product area, manage roadmap, conduct user research, drive metrics.
        *   **Senior:** Own a product line, define long-term strategy, mentor PMs, manage P&L (sometimes).
        *   **Staff/Principal:** Drive portfolio strategy, organizational alignment, innovation.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Product Management", "Product Strategy", "Roadmap Planning", "Agile Methodologies", "User Research", "Go-to-Market Strategy".
        *   **Must appear in Projects/Experience:** "Jira", "SQL", "Tableau", "User Stories", "Stakeholder Management".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus on output (features shipped) rather than outcome (impact achieved), vague descriptions.
        *   **Suggest Improvements:** Focus on metrics (adoption, retention, revenue), describe the problem solved for the user.
        *   **Rebuild Profile:** Position as a mini-CEO of the product, driving value and solving user problems.
    """,
    "DevOps Engineer": """
    **Role Analysis: DevOps Engineer**
    *   **1. Required Skills:**
        *   **Technical:** Linux/Unix, Scripting (Bash, Python), CI/CD (Jenkins, GitLab CI, GitHub Actions), Cloud (AWS, Azure, GCP), IaC (Terraform, Ansible), Containers (Docker, Kubernetes).
        *   **Soft Skills:** Collaboration, Crisis Management, Process Improvement, Automation Mindset.
    *   **2. Responsibilities:**
        *   Automate software deployment and monitoring processes.
        *   Manage cloud infrastructure and ensure high availability.
        *   Implement and maintain CI/CD pipelines.
        *   Ensure system security and compliance.
    *   **3. Technical Expectations:**
        *   Deep understanding of networking and operating systems.
        *   Experience with monitoring and logging tools (Prometheus, Grafana, ELK Stack).
        *   Knowledge of security best practices (DevSecOps).
    *   **4. Seniority Expectations:**
        *   **Junior:** Maintain existing pipelines, handle minor incidents, write simple scripts.
        *   **Mid-Level:** Build new pipelines, manage infrastructure with IaC, troubleshoot complex issues.
        *   **Senior:** Design infrastructure architecture, lead migration projects, define reliability standards (SRE).
        *   **Staff:** Define organizational DevOps strategy, optimize engineering efficiency at scale.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "DevOps", "Continuous Integration/Continuous Deployment (CI/CD)", "Infrastructure as Code (IaC)", "Cloud Computing", "Site Reliability Engineering (SRE)".
        *   **Must appear in Projects/Experience:** "AWS/Azure", "Docker", "Kubernetes", "Terraform", "Jenkins", "Linux".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Manual processes mentioned, lack of specific tool names, missing scale context.
        *   **Suggest Improvements:** Highlight automation achievements, mention specific tools and cloud platforms, quantify uptime/reliability improvements.
        *   **Rebuild Profile:** Showcase the ability to bridge the gap between development and operations through automation.
    """,
    "Machine Learning Engineer": """
    **Role Analysis: Machine Learning Engineer**
    *   **1. Required Skills:**
        *   **Technical:** Python, C++, ML Frameworks (TensorFlow, PyTorch, Keras), Big Data (Spark), MLOps (MLflow, Kubeflow), Cloud AI Services.
        *   **Soft Skills:** Research capabilities, Problem-solving, Collaboration with Data Scientists.
    *   **2. Responsibilities:**
        *   Design and build machine learning systems.
        *   Deploy ML models into production environments.
        *   Optimize models for performance and scalability.
        *   Maintain and monitor ML pipelines.
    *   **3. Technical Expectations:**
        *   Strong software engineering background combined with ML knowledge.
        *   Experience with model serving and inference optimization.
        *   Understanding of data structures and algorithms.
    *   **4. Seniority Expectations:**
        *   **Junior:** Assist in model deployment, write data processing scripts.
        *   **Mid-Level:** Build and maintain ML pipelines, optimize model performance, handle production issues.
        *   **Senior:** Design scalable ML architecture, lead MLOps initiatives, mentor team.
        *   **Staff:** Define AI engineering strategy, solve novel infrastructure challenges.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Machine Learning Engineering", "Deep Learning", "MLOps", "Model Deployment", "Natural Language Processing (NLP)", "Computer Vision".
        *   **Must appear in Projects/Experience:** "TensorFlow", "PyTorch", "Docker", "Kubernetes", "AWS SageMaker".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus only on modeling (Data Science) without engineering context, lack of production deployment experience.
        *   **Suggest Improvements:** Highlight deployment and scaling of models, mention MLOps tools used.
        *   **Rebuild Profile:** Position as an engineer who builds robust, scalable AI systems, not just models.
    """,
    "Data Engineer": """
    **Role Analysis: Data Engineer**
    *   **1. Required Skills:**
        *   **Technical:** SQL, Python/Scala, Big Data (Spark, Hadoop), Data Warehousing (Snowflake, Redshift, BigQuery), ETL/ELT pipelines (Airflow, dbt), Cloud Platforms (AWS/Azure/GCP).
        *   **Soft Skills:** Attention to detail, Logical thinking, Collaboration with Data Scientists/Analysts.
    *   **2. Responsibilities:**
        *   Design, build, and maintain scalable data pipelines.
        *   Ensure data quality, reliability, and efficiency.
        *   Optimize data retrieval and storage.
        *   Integrate new data management technologies.
    *   **3. Technical Expectations:**
        *   Proficiency in database design and modeling.
        *   Experience with stream processing (Kafka, Flink).
        *   Understanding of distributed systems.
    *   **4. Seniority Expectations:**
        *   **Junior:** Build simple ETL jobs, write SQL queries, fix pipeline failures.
        *   **Mid-Level:** Design data models, optimize pipeline performance, manage data warehouse schemas.
        *   **Senior:** Architect complex data platforms, define data governance standards, mentor team.
        *   **Staff:** Drive data strategy, solve organization-wide data accessibility problems.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Data Engineering", "ETL/ELT", "Big Data", "Data Warehousing", "Data Modeling", "Pipeline Orchestration".
        *   **Must appear in Projects/Experience:** "Apache Spark", "Airflow", "Snowflake", "Kafka", "SQL", "Python".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Confusing Data Engineering with Data Science, lack of scale context (TB/PB of data), missing orchestration tools.
        *   **Suggest Improvements:** Quantify data volume processed, mention specific ETL tools, highlight data quality improvements.
        *   **Rebuild Profile:** Focus on the architecture and reliability of data systems.
    """,
    "Cloud Engineer": """
    **Role Analysis: Cloud Engineer**
    *   **1. Required Skills:**
        *   **Technical:** Cloud Platforms (AWS, Azure, GCP), IaC (Terraform, CloudFormation), Scripting (Python, Bash), Networking (VPC, DNS, Load Balancing), Containers (Docker, Kubernetes).
        *   **Soft Skills:** Problem-solving, Adaptability, Communication (explaining infra to devs).
    *   **2. Responsibilities:**
        *   Design and deploy secure, scalable cloud infrastructure.
        *   Automate infrastructure provisioning and management.
        *   Optimize cloud costs and performance.
        *   Ensure high availability and disaster recovery.
    *   **3. Technical Expectations:**
        *   Deep understanding of cloud services (Compute, Storage, Network, Database).
        *   Knowledge of security best practices (IAM, Encryption).
        *   Experience with serverless architectures.
    *   **4. Seniority Expectations:**
        *   **Junior:** Deploy resources via console/CLI, write basic scripts, monitor systems.
        *   **Mid-Level:** Write IaC templates, manage Kubernetes clusters, optimize costs.
        *   **Senior:** Design multi-region architectures, lead migration projects, define security standards.
        *   **Staff:** Define cloud strategy, oversee multi-cloud adoption, drive platform engineering.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Cloud Computing", "AWS/Azure/GCP", "Infrastructure as Code", "Cloud Security", "Serverless", "Migration".
        *   **Must appear in Projects/Experience:** "Terraform", "Kubernetes", "Docker", "Lambda/Functions", "VPC".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Generic "Cloud" mention without specific platform details, lack of automation (IaC) experience.
        *   **Suggest Improvements:** Specify certifications (Solutions Architect), highlight automation projects, mention cost savings.
        *   **Rebuild Profile:** Position as an expert in building reliable and scalable cloud environments.
    """,
    "Cyber Security Engineer": """
    **Role Analysis: Cybersecurity Engineer**
    *   **1. Required Skills:**
        *   **Technical:** Network Security, SIEM (Splunk, ELK), Vulnerability Assessment (Nessus, Qualys), Penetration Testing (Metasploit, Burp Suite), Scripting (Python, Bash), IAM.
        *   **Soft Skills:** Integrity, Critical Thinking, Crisis Management, Communication.
    *   **2. Responsibilities:**
        *   Monitor networks for security breaches.
        *   Conduct vulnerability assessments and penetration tests.
        *   Implement security measures and incident response plans.
        *   Ensure compliance with standards (ISO 27001, GDPR, SOC2).
    *   **3. Technical Expectations:**
        *   Understanding of attack vectors and mitigation strategies.
        *   Knowledge of cryptography and PKI.
        *   Familiarity with DevSecOps practices.
    *   **4. Seniority Expectations:**
        *   **Junior:** Monitor logs, run scans, assist in incident response.
        *   **Mid-Level:** Configure firewalls/IDS, perform pentests, manage SIEM, handle incidents.
        *   **Senior:** Design security architecture, lead compliance audits, define security policies.
        *   **Staff:** CISO-level strategy, manage organizational risk, oversee security culture.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Network Security", "Vulnerability Management", "Incident Response", "Penetration Testing", "Compliance", "SIEM".
        *   **Must appear in Projects/Experience:** "Splunk", "Wireshark", "Metasploit", "Firewall", "OWASP".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Vague "Security" mention, lack of specific tool proficiency, missing compliance frameworks.
        *   **Suggest Improvements:** Mention specific tools and frameworks, highlight successful incident resolutions or audits passed.
        *   **Rebuild Profile:** Emphasize a proactive and comprehensive approach to security.
    """,
    "SRE": """
    **Role Analysis: Site Reliability Engineer (SRE)**
    *   **1. Required Skills:**
        *   **Technical:** Linux/Unix, Coding (Go, Python), Observability (Prometheus, Grafana, Datadog), Cloud (AWS/GCP), Containers (Kubernetes), Incident Management.
        *   **Soft Skills:** Calm under pressure, Root Cause Analysis, Automation Mindset.
    *   **2. Responsibilities:**
        *   Ensure system reliability and uptime (SLOs/SLAs).
        *   Automate toil and manual processes.
        *   Manage incident response and post-mortems.
        *   Build monitoring and alerting systems.
    *   **3. Technical Expectations:**
        *   Deep understanding of distributed systems failure modes.
        *   Experience with chaos engineering.
        *   Ability to debug complex production issues.
    *   **4. Seniority Expectations:**
        *   **Junior:** Handle on-call shifts, write runbooks, fix minor bugs.
        *   **Mid-Level:** Define SLIs/SLOs, build monitoring dashboards, automate deployments.
        *   **Senior:** Lead major incident response, design reliability architecture, mentor team on SRE practices.
        *   **Staff:** Define reliability strategy across the org, drive cultural shift towards SRE.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Site Reliability Engineering", "SLO/SLA", "Incident Management", "Observability", "Automation", "Chaos Engineering".
        *   **Must appear in Projects/Experience:** "Prometheus", "Grafana", "Terraform", "Kubernetes", "PagerDuty".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Confusing SRE with SysAdmin (manual work vs automation), lack of metric-driven achievements.
        *   **Suggest Improvements:** Focus on "eliminating toil", mention specific SLOs achieved, highlight automation scripts.
        *   **Rebuild Profile:** Position as a software engineer tasked with operations and reliability.
    """,
    "Mobile Developer": """
    **Role Analysis: Mobile App Developer (Android/iOS)**
    *   **1. Required Skills:**
        *   **Technical:** Swift/Objective-C (iOS), Kotlin/Java (Android), React Native/Flutter (Cross-platform), Mobile UI/UX, REST/GraphQL APIs, Local Storage (CoreData, SQLite, Realm).
        *   **Soft Skills:** User Empathy, Attention to Detail, Creativity.
    *   **2. Responsibilities:**
        *   Develop and maintain high-quality mobile applications.
        *   Ensure performance, quality, and responsiveness.
        *   Collaborate with designers to implement pixel-perfect UIs.
        *   Publish apps to App Store and Play Store.
    *   **3. Technical Expectations:**
        *   Understanding of mobile lifecycle and memory management.
        *   Experience with offline storage and caching.
        *   Knowledge of mobile design guidelines (Human Interface Guidelines, Material Design).
    *   **4. Seniority Expectations:**
        *   **Junior:** Implement UI screens, fix bugs, write unit tests.
        *   **Mid-Level:** Manage app architecture (MVVM/VIPER), handle complex API integrations, optimize performance.
        *   **Senior:** Design core app architecture, set up CI/CD for mobile, mentor team, handle app store releases.
        *   **Staff:** Define mobile strategy, oversee multiple apps, drive technical innovation.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Mobile Development", "iOS/Android", "React Native/Flutter", "Mobile UI/UX", "App Store Deployment".
        *   **Must appear in Projects/Experience:** "Swift", "Kotlin", "Xcode", "Android Studio", "Firebase".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Lack of published apps links, generic "Mobile Dev" title without platform specification.
        *   **Suggest Improvements:** Link to App Store/Play Store, mention specific architectural patterns (MVVM, Clean Architecture), highlight user ratings.
        *   **Rebuild Profile:** Showcase a portfolio of polished, user-friendly mobile applications.
    """,
    "QA Engineer": """
    **Role Analysis: QA Engineer**
    *   **1. Required Skills:**
        *   **Technical:** Automation Tools (Selenium, Cypress, Playwright, Appium), Scripting (Python, Java, JS), CI/CD Integration, API Testing (Postman, REST Assured), Load Testing (JMeter).
        *   **Soft Skills:** Attention to Detail, Critical Thinking, Communication (reporting bugs).
    *   **2. Responsibilities:**
        *   Design and implement test strategies and test plans.
        *   Develop and maintain automated test scripts.
        *   Identify, record, and track bugs.
        *   Collaborate with devs to ensure quality early in the cycle.
    *   **3. Technical Expectations:**
        *   Understanding of SDLC and STLC.
        *   Experience with BDD/TDD frameworks (Cucumber).
        *   Knowledge of performance and security testing basics.
    *   **4. Seniority Expectations:**
        *   **Junior:** Execute manual tests, write simple automation scripts, report bugs.
        *   **Mid-Level:** Build automation frameworks, integrate tests into CI/CD, perform API testing.
        *   **Senior:** Define QA strategy, lead automation initiatives, mentor team, ensure release quality.
        *   **Staff:** Drive quality culture across the org, optimize testing infrastructure.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Test Automation", "QA Engineering", "Selenium/Cypress", "API Testing", "CI/CD Integration", "Bug Tracking".
        *   **Must appear in Projects/Experience:** "Selenium", "Java/Python", "Jenkins", "Jira", "Postman".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus only on manual testing, lack of automation tools, missing CI/CD context.
        *   **Suggest Improvements:** Highlight automation percentages, mention specific frameworks built, quantify bugs caught pre-production.
        *   **Rebuild Profile:** Position as a quality advocate who uses code to ensure software reliability.
    """,
    "Business Analyst": """
    **Role Analysis: Business Analyst**
    *   **1. Required Skills:**
        *   **Technical:** SQL, Excel (Advanced), Visualization (Tableau, PowerBI), Python/R (Basic), Requirement Gathering, Process Modeling (BPMN).
        *   **Soft Skills:** Stakeholder Management, Communication, Analytical Thinking, Documentation.
    *   **2. Responsibilities:**
        *   Bridge the gap between IT and business teams.
        *   Gather and document business requirements.
        *   Analyze data to provide actionable insights.
        *   Validate solutions against requirements.
    *   **3. Technical Expectations:**
        *   Ability to translate business needs into technical specs.
        *   Proficiency in data storytelling.
        *   Understanding of agile methodologies.
    *   **4. Seniority Expectations:**
        *   **Junior:** Create reports, document meetings, assist in testing.
        *   **Mid-Level:** Lead requirement workshops, build complex dashboards, manage small projects.
        *   **Senior:** Define product strategy based on data, manage key stakeholder relationships, mentor juniors.
        *   **Staff:** Drive organizational data strategy, influence C-level decisions.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Business Analysis", "Data Visualization", "Requirement Gathering", "Stakeholder Management", "SQL", "Process Improvement".
        *   **Must appear in Projects/Experience:** "Tableau/PowerBI", "Jira", "Excel", "SQL", "User Stories".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus on tasks rather than insights, lack of specific tool names (Tableau/PowerBI).
        *   **Suggest Improvements:** Quantify impact of insights (revenue/efficiency), mention specific visualization tools used.
        *   **Rebuild Profile:** Highlight the ability to turn data and requirements into business value.
    """,
    "AI Research Scientist": """
    **Role Analysis: AI Research Scientist**
    *   **1. Required Skills:**
        *   **Technical:** Deep Learning (PyTorch/TensorFlow), Mathematics (Linear Algebra, Calculus, Probability), Academic Writing, Python, C++.
        *   **Soft Skills:** Critical Thinking, Persistence, Communication (publishing papers).
    *   **2. Responsibilities:**
        *   Conduct cutting-edge research in AI/ML.
        *   Publish papers in top conferences (NeurIPS, ICML, CVPR).
        *   Develop novel algorithms and models.
        *   Collaborate with engineering teams to transfer research to production.
    *   **3. Technical Expectations:**
        *   Deep theoretical understanding of ML algorithms.
        *   Experience with large-scale model training.
        *   Ability to read and implement research papers.
    *   **4. Seniority Expectations:**
        *   **Junior:** Implement experiments, assist senior researchers.
        *   **Mid-Level:** Lead research projects, publish papers, mentor interns.
        *   **Senior:** Define research agenda, lead large research teams, influence field direction.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Deep Learning", "Computer Vision/NLP", "Research", "PyTorch", "Mathematics".
        *   **Must appear in Projects/Experience:** "NeurIPS/ICML", "Publications", "Novel Algorithms".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Lack of publications, focus on application rather than innovation.
        *   **Suggest Improvements:** Highlight publications and patents, mention specific novel contributions.
        *   **Rebuild Profile:** Position as a thought leader and innovator in the AI field.
    """,
    "Hardware Engineer": """
    **Role Analysis: Hardware Engineer**
    *   **1. Required Skills:**
        *   **Technical:** PCB Design, Circuit Analysis, Verilog/VHDL, C/C++ (Embedded), Microcontrollers (ARM, AVR), FPGA, Lab Equipment (Oscilloscopes).
        *   **Soft Skills:** Attention to Detail, Problem-solving, Patience.
    *   **2. Responsibilities:**
        *   Design and test electronic circuits and systems.
        *   Develop firmware for embedded systems.
        *   Debug hardware-software integration issues.
        *   Ensure compliance with safety and EMI/EMC standards.
    *   **3. Technical Expectations:**
        *   Understanding of digital and analog electronics.
        *   Experience with RTOS.
        *   Knowledge of communication protocols (I2C, SPI, UART, CAN).
    *   **4. Seniority Expectations:**
        *   **Junior:** Test boards, write basic firmware, assist in design.
        *   **Mid-Level:** Design PCBs, write complex drivers, handle board bring-up.
        *   **Senior:** Architect system hardware, lead design reviews, manage manufacturing transfer.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Embedded Systems", "PCB Design", "Firmware", "Verilog/VHDL", "Circuit Design".
        *   **Must appear in Projects/Experience:** "Altium", "C/C++", "FPGA", "ARM", "RTOS".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Lack of specific hardware/chip mentions, vague "electronics" skills.
        *   **Suggest Improvements:** Mention specific microcontrollers/FPGAs used, highlight successful product launches.
        *   **Rebuild Profile:** Showcase the ability to build physical systems that work reliably.
    """,
    "Blockchain Developer": """
    **Role Analysis: Blockchain Developer**
    *   **1. Required Skills:**
        *   **Technical:** Solidity (Ethereum), Rust (Solana), Smart Contracts, Web3.js/Ethers.js, Cryptography, Distributed Ledgers.
        *   **Soft Skills:** Security Mindset, Attention to Detail, Innovation.
    *   **2. Responsibilities:**
        *   Design and develop decentralized applications (dApps).
        *   Write and audit secure smart contracts.
        *   Integrate blockchain with frontend/backend systems.
        *   Research and implement new blockchain protocols.
    *   **3. Technical Expectations:**
        *   Deep understanding of consensus mechanisms (PoW, PoS).
        *   Knowledge of gas optimization and security vulnerabilities (Reentrancy).
        *   Experience with DeFi or NFT standards.
    *   **4. Seniority Expectations:**
        *   **Junior:** Write simple contracts, build frontend for dApps.
        *   **Mid-Level:** Optimize contracts, handle complex logic, audit code.
        *   **Senior:** Architect protocol-level solutions, lead security audits, design tokenomics.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Blockchain", "Smart Contracts", "Solidity", "Web3", "DeFi/NFT".
        *   **Must appear in Projects/Experience:** "Ethereum", "Hardhat/Truffle", "Rust", "Cryptography".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus on trading rather than building, lack of security auditing mentions.
        *   **Suggest Improvements:** Highlight deployed contracts (with addresses), mention security audits passed.
        *   **Rebuild Profile:** Position as a builder of the decentralized web.
    """,
    "Game Developer": """
    **Role Analysis: Game Developer**
    *   **1. Required Skills:**
        *   **Technical:** C++ (Unreal), C# (Unity), 3D Math (Linear Algebra), Graphics Programming (OpenGL/DirectX/Vulkan), Physics Engines, AI for Games.
        *   **Soft Skills:** Creativity, Collaboration (with artists/designers), Passion for Gaming.
    *   **2. Responsibilities:**
        *   Implement gameplay mechanics and systems.
        *   Optimize game performance and memory usage.
        *   Develop tools for content creators.
        *   Collaborate to deliver a fun player experience.
    *   **3. Technical Expectations:**
        *   Understanding of game loops and rendering pipelines.
        *   Experience with multiplayer networking.
        *   Knowledge of shaders and visual effects.
    *   **4. Seniority Expectations:**
        *   **Junior:** Implement gameplay features, fix bugs.
        *   **Mid-Level:** Optimize rendering, handle networking, design systems.
        *   **Senior:** Architect game engine subsystems, lead technical direction, mentor team.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Game Development", "Unity/Unreal Engine", "C++/C#", "3D Mathematics", "Graphics Programming".
        *   **Must appear in Projects/Experience:** "Unity", "Unreal", "OpenGL", "Shaders".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Lack of portfolio/demo reel, generic "programming" skills without game context.
        *   **Suggest Improvements:** Link to itch.io/Steam page, mention specific engine subsystems worked on.
        *   **Rebuild Profile:** Showcase the ability to create immersive interactive experiences.
    """,
    "Network Engineer": """
    **Role Analysis: Network Engineer**
    *   **1. Required Skills:**
        *   **Technical:** Routing & Switching (Cisco/Juniper), Firewalls (Palo Alto/Fortinet), VPN, DNS, TCP/IP, Network Automation (Python/Ansible), Cloud Networking.
        *   **Soft Skills:** Troubleshooting, Analytical Thinking, Availability (On-call).
    *   **2. Responsibilities:**
        *   Design, implement, and manage network infrastructure.
        *   Monitor network performance and security.
        *   Troubleshoot connectivity issues.
        *   Configure routers, switches, and firewalls.
    *   **3. Technical Expectations:**
        *   Deep understanding of OSI model and protocols (BGP, OSPF).
        *   Experience with SD-WAN and MPLS.
        *   Knowledge of network security best practices.
    *   **4. Seniority Expectations:**
        *   **Junior:** Monitor alerts, configure access ports, basic troubleshooting.
        *   **Mid-Level:** Configure routing protocols, manage firewalls, handle complex outages.
        *   **Senior:** Architect global network infrastructure, lead automation, design disaster recovery.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Network Engineering", "Routing & Switching", "Firewall Configuration", "TCP/IP", "CCNA/CCNP".
        *   **Must appear in Projects/Experience:** "Cisco", "Juniper", "BGP/OSPF", "VPN", "Wireshark".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Lack of certifications (CCNA/CCNP), focus on helpdesk tasks.
        *   **Suggest Improvements:** Highlight specific protocols configured, mention scale of network managed.
        *   **Rebuild Profile:** Position as an architect of reliable connectivity.
    """,
    "Scrum Master": """
    **Role Analysis: Scrum Master**
    *   **1. Required Skills:**
        *   **Technical:** Agile Frameworks (Scrum, Kanban, SAFe), Jira/Confluence, Facilitation, Conflict Resolution, Metrics (Velocity, Burndown).
        *   **Soft Skills:** Servant Leadership, Empathy, Communication, Coaching.
    *   **2. Responsibilities:**
        *   Facilitate Agile ceremonies (Daily Standup, Sprint Planning, Retro).
        *   Remove impediments for the team.
        *   Coach the team and organization on Agile practices.
        *   Track and report team metrics.
    *   **3. Technical Expectations:**
        *   Deep understanding of Agile values and principles.
        *   Ability to handle resistance to change.
        *   Experience with scaling Agile.
    *   **4. Seniority Expectations:**
        *   **Junior:** Facilitate meetings, update Jira.
        *   **Mid-Level:** Coach team on improvement, handle conflict, manage dependencies.
        *   **Senior:** Coach multiple teams, drive organizational Agile transformation, mentor other Scrum Masters.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Agile Methodologies", "Scrum", "Kanban", "Servant Leadership", "Facilitation", "CSM/PSM".
        *   **Must appear in Projects/Experience:** "Jira", "Sprint Planning", "Retrospectives", "Velocity".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Acting as a project manager (command & control) instead of servant leader.
        *   **Suggest Improvements:** Highlight team improvements (velocity increased, bugs reduced), mention coaching achievements.
        *   **Rebuild Profile:** Position as a catalyst for team efficiency and happiness.
    """,
    "Solutions Architect": """
    **Role Analysis: Solutions Architect**
    *   **1. Required Skills:**
        *   **Technical:** Cloud Architecture (AWS/Azure), System Design, Integration Patterns, Security, Enterprise Architecture, Pre-sales support.
        *   **Soft Skills:** Communication, Persuasion, Business Acumen, Presentation.
    *   **2. Responsibilities:**
        *   Design technical solutions to meet business requirements.
        *   Bridge the gap between business problems and technology.
        *   Guide development teams on best practices.
        *   Assist sales teams with technical proposals.
    *   **3. Technical Expectations:**
        *   Broad knowledge of technology landscape.
        *   Ability to design scalable, secure, and cost-effective systems.
        *   Experience with legacy modernization.
    *   **4. Seniority Expectations:**
        *   **Junior:** Assist in creating diagrams, research technologies.
        *   **Mid-Level:** Design components of a solution, lead small engagements.
        *   **Senior:** Architect complex enterprise solutions, lead digital transformations, advise C-level execs.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Solutions Architecture", "Cloud Computing", "System Design", "Enterprise Integration", "Pre-sales".
        *   **Must appear in Projects/Experience:** "AWS/Azure Certified", "Microservices", "API Design".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Too focused on coding, lack of high-level design, missing business context.
        *   **Suggest Improvements:** Highlight successful solution deliveries, mention cost savings or revenue enabled.
        *   **Rebuild Profile:** Position as a strategic technical advisor.
    """,
    "Technical Writer": """
    **Role Analysis: Technical Writer**
    *   **1. Required Skills:**
        *   **Technical:** Technical Writing, Documentation Tools (Markdown, DITA, MadCap Flare), API Documentation (Swagger/OpenAPI), Git, Basic Coding.
        *   **Soft Skills:** Clarity, Attention to Detail, Empathy for the Reader, Curiosity.
    *   **2. Responsibilities:**
        *   Create clear and concise technical documentation (manuals, guides, API docs).
        *   Collaborate with SMEs (Subject Matter Experts) to gather information.
        *   Edit and proofread content.
        *   Manage documentation lifecycle.
    *   **3. Technical Expectations:**
        *   Ability to understand complex technical concepts.
        *   Experience with docs-as-code workflows.
        *   Knowledge of style guides (Microsoft, Google).
    *   **4. Seniority Expectations:**
        *   **Junior:** Write basic articles, edit existing docs.
        *   **Mid-Level:** Plan documentation sets, document APIs, manage small projects.
        *   **Senior:** Define information architecture, lead documentation strategy, mentor writers.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Technical Writing", "API Documentation", "Content Strategy", "Information Architecture", "Markdown".
        *   **Must appear in Projects/Experience:** "Swagger", "Jira", "Git", "Confluence".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Generic writing samples, lack of technical depth.
        *   **Suggest Improvements:** Link to public documentation portfolio, mention tools used (docs-as-code).
        *   **Rebuild Profile:** Position as a bridge between complex technology and users.
    """,
    "Data Analyst": """
    **Role Analysis: Data Analyst**
    *   **1. Required Skills:**
        *   **Technical:** SQL, Excel (Advanced), Visualization (Tableau, PowerBI), Python/R (Basic), Data Cleaning, Statistical Analysis.
        *   **Soft Skills:** Analytical Thinking, Attention to Detail, Communication (Storytelling with Data), Curiosity.
    *   **2. Responsibilities:**
        *   Collect, process, and perform statistical analyses of data.
        *   Identify trends and patterns in complex data sets.
        *   Create visualizations and reports for stakeholders.
        *   Maintain databases and data systems.
    *   **3. Technical Expectations:**
        *   Proficiency in writing complex SQL queries.
        *   Ability to create interactive dashboards.
        *   Understanding of data warehousing concepts.
    *   **4. Seniority Expectations:**
        *   **Junior:** Clean data, run basic reports, maintain dashboards.
        *   **Mid-Level:** Identify trends, provide actionable insights, automate reporting.
        *   **Senior:** Define data strategy for the team, mentor juniors, influence business decisions with data.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Data Analysis", "SQL", "Data Visualization", "Statistical Analysis", "Reporting", "Business Intelligence".
        *   **Must appear in Projects/Experience:** "Tableau/PowerBI", "Excel", "Python/R", "Dashboards".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Listing tools without context, lack of business impact (what did the analysis lead to?).
        *   **Suggest Improvements:** Quantify the impact of insights (e.g., "Identified efficiency gap saving $10k/month"), mention specific visualization types.
        *   **Rebuild Profile:** Highlight the ability to turn raw data into business value.
    """,
    "UI/UX Designer": """
    **Role Analysis: UI/UX Designer**
    *   **1. Required Skills:**
        *   **Technical:** Figma, Adobe Creative Suite (Xd, Illustrator, Photoshop), Prototyping, Wireframing, User Research, Usability Testing, HTML/CSS (Basic).
        *   **Soft Skills:** Empathy, Creativity, Collaboration, Communication, Problem-solving.
    *   **2. Responsibilities:**
        *   Conduct user research and evaluate user feedback.
        *   Create wireframes, storyboards, user flows, and process flows.
        *   Design high-fidelity UI mockups and prototypes.
        *   Collaborate with developers to ensure design feasibility.
    *   **3. Technical Expectations:**
        *   Strong portfolio demonstrating design process (not just final screens).
        *   Understanding of design systems and accessibility standards (WCAG).
        *   Knowledge of mobile-first and responsive design.
    *   **4. Seniority Expectations:**
        *   **Junior:** Execute designs based on guidelines, assist in research.
        *   **Mid-Level:** Lead design for features, conduct usability tests, maintain design systems.
        *   **Senior:** Define product design strategy, mentor designers, collaborate with product leadership.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "User Interface (UI)", "User Experience (UX)", "Wireframing", "Prototyping", "User Research", "Design Systems".
        *   **Must appear in Projects/Experience:** "Figma", "Adobe Xd", "Usability Testing", "Personas", "User Flows".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus on aesthetics over usability, lack of process description (the "why"), missing portfolio link.
        *   **Suggest Improvements:** Include a link to a portfolio, describe the problem-solving process (Double Diamond), mention impact on user metrics (conversion, retention).
        *   **Rebuild Profile:** Position as a problem solver who designs intuitive and beautiful experiences.
    """,
    "Technical Program Manager": """
    **Role Analysis: Technical Program Manager (TPM)**
    *   **1. Required Skills:**
        *   **Technical:** SDLC, Agile/Scrum, Cloud/Infrastructure knowledge, API basics, System Design understanding.
        *   **Soft Skills:** Leadership, Stakeholder Management, Risk Management, Communication, Negotiation.
    *   **2. Responsibilities:**
        *   Manage complex cross-functional technical programs.
        *   Define program roadmap and milestones.
        *   Identify and mitigate risks.
        *   Bridge the gap between engineering and business teams.
    *   **3. Technical Expectations:**
        *   Ability to understand technical architecture and trade-offs.
        *   Experience with project management tools (Jira, Asana).
        *   Proficiency in data analysis for program tracking.
    *   **4. Seniority Expectations:**
        *   **Junior:** Manage small projects, track tasks, report status.
        *   **Mid-Level:** Drive programs across multiple teams, handle dependencies, manage risks.
        *   **Senior/Principal:** Lead organizational initiatives, define program management standards, influence executive strategy.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Technical Program Management", "Cross-functional Leadership", "Risk Management", "Agile", "Roadmap Planning", "SDLC".
        *   **Must appear in Projects/Experience:** "Jira", "Stakeholder Management", "Cloud", "Architecture", "Delivery".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Acting as a scribe rather than a leader, lack of technical depth, vague outcomes.
        *   **Suggest Improvements:** Highlight "unblocking" teams, mention specific technical challenges overcome, quantify program scale.
        *   **Rebuild Profile:** Position as a strategic leader who drives technical execution.
    """,
    "TPM": """
    **Role Analysis: Technical Program Manager (TPM)**
    *   **1. Required Skills:**
        *   **Technical:** SDLC, Agile/Scrum, Cloud/Infrastructure knowledge, API basics, System Design understanding.
        *   **Soft Skills:** Leadership, Stakeholder Management, Risk Management, Communication, Negotiation.
    *   **2. Responsibilities:**
        *   Manage complex cross-functional technical programs.
        *   Define program roadmap and milestones.
        *   Identify and mitigate risks.
        *   Bridge the gap between engineering and business teams.
    *   **3. Technical Expectations:**
        *   Ability to understand technical architecture and trade-offs.
        *   Experience with project management tools (Jira, Asana).
        *   Proficiency in data analysis for program tracking.
    *   **4. Seniority Expectations:**
        *   **Junior:** Manage small projects, track tasks, report status.
        *   **Mid-Level:** Drive programs across multiple teams, handle dependencies, manage risks.
        *   **Senior/Principal:** Lead organizational initiatives, define program management standards, influence executive strategy.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Technical Program Management", "Cross-functional Leadership", "Risk Management", "Agile", "Roadmap Planning", "SDLC".
        *   **Must appear in Projects/Experience:** "Jira", "Stakeholder Management", "Cloud", "Architecture", "Delivery".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Acting as a scribe rather than a leader, lack of technical depth, vague outcomes.
        *   **Suggest Improvements:** Highlight "unblocking" teams, mention specific technical challenges overcome, quantify program scale.
        *   **Rebuild Profile:** Position as a strategic leader who drives technical execution.
    """,
    "Project Manager": """
    **Role Analysis: Project Manager**
    *   **1. Required Skills:**
        *   **Technical:** Project Management Methodologies (Waterfall, Agile, Hybrid), Tools (MS Project, Jira, Asana), Budgeting, Scheduling.
        *   **Soft Skills:** Organization, Leadership, Communication, Conflict Resolution, Time Management.
    *   **2. Responsibilities:**
        *   Plan, execute, and close projects.
        *   Manage project scope, time, and cost.
        *   Coordinate project team and resources.
        *   Ensure project quality and stakeholder satisfaction.
    *   **3. Technical Expectations:**
        *   PMP or PRINCE2 certification (preferred).
        *   Ability to create Gantt charts and resource plans.
        *   Risk management and mitigation planning.
    *   **4. Seniority Expectations:**
        *   **Junior:** Assist in project planning, track tasks, organize meetings.
        *   **Mid-Level:** Manage medium-sized projects independently, handle budget, manage stakeholders.
        *   **Senior:** Manage large/complex portfolios, mentor PMs, define PMO processes.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Project Management", "Scope Management", "Budgeting", "Risk Management", "Stakeholder Communication", "PMP".
        *   **Must appear in Projects/Experience:** "Jira/Asana", "Gantt Charts", "Resource Planning", "Delivery".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus on administrative tasks, lack of ownership, missing project metrics (on time, on budget).
        *   **Suggest Improvements:** Quantify project budget and team size, highlight successful delivery metrics, mention certifications.
        *   **Rebuild Profile:** Position as a reliable leader who delivers results.
    """,
    "Recruiter": """
    **Role Analysis: Recruiter / Talent Acquisition**
    *   **1. Required Skills:**
        *   **Technical:** ATS (Greenhouse, Lever, Workday), LinkedIn Recruiter, Boolean Search, Sourcing, Interviewing.
        *   **Soft Skills:** Communication, Relationship Building, Sales/Persuasion, Empathy, Time Management.
    *   **2. Responsibilities:**
        *   Source and attract candidates for open positions.
        *   Screen resumes and conduct initial interviews.
        *   Coordinate interview process with hiring managers.
        *   Manage offers and negotiation.
    *   **3. Technical Expectations:**
        *   Understanding of the full recruitment lifecycle.
        *   Ability to build talent pipelines.
        *   Knowledge of employment laws and diversity hiring practices.
    *   **4. Seniority Expectations:**
        *   **Junior:** Schedule interviews, source candidates, screen resumes.
        *   **Mid-Level:** Manage full-cycle recruiting for specific roles, partner with hiring managers.
        *   **Senior:** Lead recruiting for critical/executive roles, define hiring strategy, mentor team.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Talent Acquisition", "Full-cycle Recruiting", "Sourcing", "Candidate Experience", "Stakeholder Management", "Diversity Hiring".
        *   **Must appear in Projects/Experience:** "LinkedIn Recruiter", "ATS", "Boolean Search", "Hiring Goals".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Vague "hiring" mentions, lack of metrics (time-to-fill, hires per quarter).
        *   **Suggest Improvements:** Quantify hires made, mention specific difficult roles filled, highlight improvements in time-to-hire or quality-of-hire.
        *   **Rebuild Profile:** Position as a strategic partner in building high-performing teams.
    """,
    "Talent Acquisition": """
    **Role Analysis: Recruiter / Talent Acquisition**
    *   **1. Required Skills:**
        *   **Technical:** ATS (Greenhouse, Lever, Workday), LinkedIn Recruiter, Boolean Search, Sourcing, Interviewing.
        *   **Soft Skills:** Communication, Relationship Building, Sales/Persuasion, Empathy, Time Management.
    *   **2. Responsibilities:**
        *   Source and attract candidates for open positions.
        *   Screen resumes and conduct initial interviews.
        *   Coordinate interview process with hiring managers.
        *   Manage offers and negotiation.
    *   **3. Technical Expectations:**
        *   Understanding of the full recruitment lifecycle.
        *   Ability to build talent pipelines.
        *   Knowledge of employment laws and diversity hiring practices.
    *   **4. Seniority Expectations:**
        *   **Junior:** Schedule interviews, source candidates, screen resumes.
        *   **Mid-Level:** Manage full-cycle recruiting for specific roles, partner with hiring managers.
        *   **Senior:** Lead recruiting for critical/executive roles, define hiring strategy, mentor team.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Talent Acquisition", "Full-cycle Recruiting", "Sourcing", "Candidate Experience", "Stakeholder Management", "Diversity Hiring".
        *   **Must appear in Projects/Experience:** "LinkedIn Recruiter", "ATS", "Boolean Search", "Hiring Goals".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Vague "hiring" mentions, lack of metrics (time-to-fill, hires per quarter).
        *   **Suggest Improvements:** Quantify hires made, mention specific difficult roles filled, highlight improvements in time-to-hire or quality-of-hire.
        *   **Rebuild Profile:** Position as a strategic partner in building high-performing teams.
    """,
    "Customer Success Manager": """
    **Role Analysis: Customer Success Manager (CSM)**
    *   **1. Required Skills:**
        *   **Technical:** CRM (Salesforce, HubSpot), Product Knowledge, Data Analysis (Usage metrics), Onboarding tools.
        *   **Soft Skills:** Empathy, Communication, Relationship Building, Problem-solving, Persuasion (Upselling).
    *   **2. Responsibilities:**
        *   Manage a portfolio of customers and ensure their success/retention.
        *   Onboard new customers and drive product adoption.
        *   Identify upsell and cross-sell opportunities.
        *   Act as the voice of the customer to the product team.
    *   **3. Technical Expectations:**
        *   Understanding of SaaS metrics (Churn, NRR, ARR/MRR).
        *   Ability to conduct Quarterly Business Reviews (QBRs).
        *   Proficiency in troubleshooting basic product issues.
    *   **4. Seniority Expectations:**
        *   **Junior:** Support smaller accounts, handle onboarding, answer queries.
        *   **Mid-Level:** Manage mid-market/enterprise accounts, drive renewals, conduct QBRs.
        *   **Senior:** Manage strategic/key accounts, define CS strategy, mentor team.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Customer Success", "Account Management", "Retention", "Churn Reduction", "Onboarding", "Upselling".
        *   **Must appear in Projects/Experience:** "Salesforce", "QBR", "SaaS", "Net Revenue Retention (NRR)".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus on support (reactive) rather than success (proactive), lack of retention/growth metrics.
        *   **Suggest Improvements:** Quantify retention rates and upsell revenue, mention specific strategic wins with clients.
        *   **Rebuild Profile:** Position as a trusted advisor who drives value for customers.
    """,
    "Marketing Manager": """
    **Role Analysis: Marketing Manager / Digital Marketing**
    *   **1. Required Skills:**
        *   **Technical:** SEO/SEM, Google Analytics, Social Media Management, Email Marketing (Mailchimp, HubSpot), Content Management Systems (CMS), CRM.
        *   **Soft Skills:** Creativity, Analytical Thinking, Communication, Strategic Planning.
    *   **2. Responsibilities:**
        *   Develop and implement marketing strategies.
        *   Manage digital marketing campaigns across channels.
        *   Analyze market trends and competitor activity.
        *   Measure and report on campaign performance (ROI).
    *   **3. Technical Expectations:**
        *   Understanding of the marketing funnel.
        *   Experience with paid advertising (Google Ads, Facebook Ads).
        *   Proficiency in content creation and copywriting.
    *   **4. Seniority Expectations:**
        *   **Junior:** Execute campaign tasks, manage social media, write copy.
        *   **Mid-Level:** Manage specific channels or campaigns, analyze performance, manage budget.
        *   **Senior:** Define overall marketing strategy, manage brand, lead marketing team.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Digital Marketing", "SEO/SEM", "Content Strategy", "Campaign Management", "Brand Management", "Analytics".
        *   **Must appear in Projects/Experience:** "Google Analytics", "ROI", "Lead Generation", "Social Media".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus on activities ("posted on social media") rather than results ("grew following by X%"), lack of specific tool mentions.
        *   **Suggest Improvements:** Quantify campaign results (leads, conversion, ROI), mention specific channels mastered.
        *   **Rebuild Profile:** Position as a growth driver who combines creativity with data.
    """,
    "Digital Marketing": """
    **Role Analysis: Marketing Manager / Digital Marketing**
    *   **1. Required Skills:**
        *   **Technical:** SEO/SEM, Google Analytics, Social Media Management, Email Marketing (Mailchimp, HubSpot), Content Management Systems (CMS), CRM.
        *   **Soft Skills:** Creativity, Analytical Thinking, Communication, Strategic Planning.
    *   **2. Responsibilities:**
        *   Develop and implement marketing strategies.
        *   Manage digital marketing campaigns across channels.
        *   Analyze market trends and competitor activity.
        *   Measure and report on campaign performance (ROI).
    *   **3. Technical Expectations:**
        *   Understanding of the marketing funnel.
        *   Experience with paid advertising (Google Ads, Facebook Ads).
        *   Proficiency in content creation and copywriting.
    *   **4. Seniority Expectations:**
        *   **Junior:** Execute campaign tasks, manage social media, write copy.
        *   **Mid-Level:** Manage specific channels or campaigns, analyze performance, manage budget.
        *   **Senior:** Define overall marketing strategy, manage brand, lead marketing team.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Digital Marketing", "SEO/SEM", "Content Strategy", "Campaign Management", "Brand Management", "Analytics".
        *   **Must appear in Projects/Experience:** "Google Analytics", "ROI", "Lead Generation", "Social Media".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Focus on activities ("posted on social media") rather than results ("grew following by X%"), lack of specific tool mentions.
        *   **Suggest Improvements:** Quantify campaign results (leads, conversion, ROI), mention specific channels mastered.
        *   **Rebuild Profile:** Position as a growth driver who combines creativity with data.
    """,
    "Sales Engineer": """
    **Role Analysis: Sales Engineer / Pre-Sales**
    *   **1. Required Skills:**
        *   **Technical:** Product Knowledge, Technical Demo skills, Solution Architecture basics, Industry-specific tech stack.
        *   **Soft Skills:** Presentation, Persuasion, Active Listening, Problem-solving, Relationship Building.
    *   **2. Responsibilities:**
        *   Deliver technical presentations and product demonstrations.
        *   Partner with sales reps to close deals.
        *   Answer technical questions and RFPs/RFIs.
        *   Gather customer requirements and propose solutions.
    *   **3. Technical Expectations:**
        *   Ability to explain complex technical concepts to non-technical audiences.
        *   Experience with POCs (Proof of Concepts).
        *   Understanding of the sales cycle.
    *   **4. Seniority Expectations:**
        *   **Junior:** Support demos, answer basic technical questions, learn product.
        *   **Mid-Level:** Lead demos for mid-market deals, manage POCs, customize solutions.
        *   **Senior:** Lead complex enterprise deals, mentor team, influence product roadmap based on market feedback.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Sales Engineering", "Pre-Sales", "Technical Demos", "Solution Selling", "RFP/RFI", "POC".
        *   **Must appear in Projects/Experience:** "CRM", "Deal Support", "Customer Requirements", "Presentation".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Too technical (ignoring sales aspect) or too salesy (lacking technical depth), lack of revenue impact.
        *   **Suggest Improvements:** Quantify revenue influenced/closed, mention specific complex deals won, highlight technical wins in POCs.
        *   **Rebuild Profile:** Position as the technical bridge that wins customer trust and deals.
    """,
    "Financial Analyst": """
    **Role Analysis: Financial Analyst**
    *   **1. Required Skills:**
        *   **Technical:** Excel (Advanced - Macros, VBA), Financial Modeling, SQL, ERP Systems (SAP, Oracle), Data Visualization.
        *   **Soft Skills:** Analytical Thinking, Attention to Detail, Communication, Business Acumen.
    *   **2. Responsibilities:**
        *   Analyze financial data and trends.
        *   Create financial models for forecasting and budgeting.
        *   Prepare financial reports and presentations.
        *   Evaluate investment opportunities.
    *   **3. Technical Expectations:**
        *   Deep understanding of accounting principles (GAAP/IFRS).
        *   Proficiency in 3-statement modeling.
        *   Ability to analyze variance (Actual vs. Budget).
    *   **4. Seniority Expectations:**
        *   **Junior:** Data entry, basic reporting, assist in month-end close.
        *   **Mid-Level:** Build complex models, lead budgeting process for a division, provide strategic recommendations.
        *   **Senior:** Oversee financial planning for the org, advise CFO/execs, lead M&A analysis.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Financial Analysis", "Financial Modeling", "Forecasting", "Budgeting", "Variance Analysis", "GAAP/IFRS".
        *   **Must appear in Projects/Experience:** "Excel", "SAP/Oracle", "Bloomberg", "Valuation".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** Listing tasks ("prepared reports") without impact, lack of modeling complexity.
        *   **Suggest Improvements:** Quantify cost savings or revenue growth identified, mention specific complex models built, highlight accuracy of forecasts.
        *   **Rebuild Profile:** Position as a strategic partner who drives financial health.
    """,
    "Operations Manager": """
    **Role Analysis: Operations Manager**
    *   **1. Required Skills:**
        *   **Technical:** Process Improvement (Six Sigma, Lean), Project Management, Data Analysis, ERP/CRM systems, Supply Chain basics.
        *   **Soft Skills:** Leadership, Problem-solving, Decision-making, Adaptability, Communication.
    *   **2. Responsibilities:**
        *   Oversee daily operations and ensure efficiency.
        *   Manage budgets and resources.
        *   Implement policies and procedures.
        *   Monitor performance metrics and drive improvements.
    *   **3. Technical Expectations:**
        *   Ability to optimize workflows and reduce waste.
        *   Experience with inventory management or logistics (if applicable).
        *   Proficiency in operational reporting.
    *   **4. Seniority Expectations:**
        *   **Junior:** Supervise a small team, monitor specific processes.
        *   **Mid-Level:** Manage a department, drive process changes, manage P&L for the unit.
        *   **Senior:** Oversee operations for the entire org/region, define operational strategy, drive organizational efficiency.
    *   **5. ATS Keyword Rules:**
        *   **Must appear in Skills/Summary:** "Operations Management", "Process Improvement", "Strategic Planning", "Team Leadership", "Budget Management", "Efficiency".
        *   **Must appear in Projects/Experience:** "KPIs", "SOPs", "Six Sigma/Lean", "P&L".
    *   **6. Evaluation Guide for the AI:**
        *   **Identify Weaknesses:** General "management" descriptions without specifics, lack of efficiency metrics.
        *   **Suggest Improvements:** Quantify efficiency gains (time/cost saved), mention specific processes improved, highlight team size managed.
        *   **Rebuild Profile:** Position as an efficiency expert who drives operational excellence.
    """
}

def get_role_prompt(role_name):
    """
    Retrieves the prompt for a specific job role.
    If the role is not found, returns a generic prompt.
    Handles case-insensitive matching and partial matches (e.g., "Senior Software Engineer" -> "Software Engineer").
    """
    if not role_name:
        return "Role specific data not available. Analyze based on general industry standards for this role."

    role_name_lower = role_name.lower().strip()

    # 1. Direct lookup
    if role_name in ROLE_PROMPTS:
        logger.info("Selected role prompt via direct match: %s", safe_log_text(role_name))
        return ROLE_PROMPTS[role_name]

    # 2. Case-insensitive lookup
    for key, prompt in ROLE_PROMPTS.items():
        if key.lower() == role_name_lower:
            logger.info(
                "Selected role prompt via case-insensitive match: %s",
                safe_log_text(key),
            )
            return prompt

    # 3. Substring lookup (Key in Input)
    # e.g. Input: "Senior Software Engineer" -> Key "Software Engineer" is in input.
    matched_prompt = None
    longest_match_len = 0
    matched_key = None

    for key, prompt in ROLE_PROMPTS.items():
        key_lower = key.lower()
        if key_lower in role_name_lower:
            if len(key_lower) > longest_match_len:
                longest_match_len = len(key_lower)
                matched_prompt = prompt
                matched_key = key

    if matched_prompt:
        logger.info(
            "Selected role prompt via substring match: %s",
            safe_log_text(matched_key),
        )
        return matched_prompt

    # 4. Reverse Substring lookup (Input in Key)
    # e.g. Input: "Software" -> Key "Software Engineer" contains input.
    # Prioritize keys that START with the input.
    reverse_matched_prompt = None
    reverse_matched_key = None
    # We want the shortest key that matches to avoid over-matching (e.g. "Eng" matching "Engineering Manager" vs "Engineer")
    # But actually, "Software" matching "Software Engineer" is good.
    # Let's collect all matches and pick the best one.
    matches = []

    for key, prompt in ROLE_PROMPTS.items():
        key_lower = key.lower()
        if role_name_lower in key_lower:
            matches.append(key)

    if matches:
        # Sort matches:
        # 1. Starts with input (priority)
        # 2. Length of key (shorter is usually more generic/better match for short input)
        def sort_key(k):
            k_lower = k.lower()
            starts_with = k_lower.startswith(role_name_lower)
            return (not starts_with, len(k)) # False < True, so starts_with comes first

        matches.sort(key=sort_key)
        best_match_key = matches[0]
        logger.info(
            "Selected role prompt via reverse substring match: %s",
            safe_log_text(best_match_key),
        )
        return ROLE_PROMPTS[best_match_key]

    # 5. Fuzzy lookup (Handle typos)
    # Use difflib to find close matches
    # cutoff=0.6 means 60% similarity required.
    close_matches = difflib.get_close_matches(role_name, ROLE_PROMPTS.keys(), n=1, cutoff=0.6)
    
    if close_matches:
        matched_key = close_matches[0]
        logger.info(
            "Selected role prompt via fuzzy match: matched=%s input=%s",
            safe_log_text(matched_key),
            safe_log_text(role_name),
        )
        return ROLE_PROMPTS[matched_key]

    logger.info(
        "No specific role prompt found for input=%s; using default.",
        safe_log_text(role_name),
    )
    return "Role specific data not available. Analyze based on general industry standards for this role."
