
import difflib

from .logging_utils import get_logger, safe_log_text

logger = get_logger(__name__)
COMPANY_PROMPTS = {
    "Google": """
    **Company Analysis: Google**
    *   **Tone:** Innovative, intellectual, curious, "Googley" (humble, collaborative, friendly).
    *   **Hiring Culture:** Focus on General Cognitive Ability (GCA), role-related knowledge, leadership, and "Googleyness". Highly values problem-solving skills and ability to handle ambiguity.
    *   **Preferred Communication Style:** Data-driven but conversational, structured thinking, clear articulation of complex ideas.
    *   **Expected Values:** Focus on the user, democracy on the web, fast is better than slow, great just isn't good enough.
    *   **Typical Role Expectations:** Engineering excellence, scalability, understanding of distributed systems, ability to write clean and efficient code.
    *   **Keywords:** Scalability, Distributed Systems, Python, Go, C++, AI/ML, Big Data, MapReduce, Kubernetes, Borg, GCA.
    """,
    "Amazon": """
    **Company Analysis: Amazon**
    *   **Tone:** Pragmatic, concise, data-driven, intense.
    *   **Hiring Culture:** Strictly adheres to the 16 Leadership Principles. "Bar Raiser" interviews are critical.
    *   **Preferred Communication Style:** The STAR method (Situation, Task, Action, Result) is mandatory. Written communication (6-page memos) is preferred over presentations.
    *   **Expected Values:** Customer Obsession, Ownership, Bias for Action, Dive Deep, Frugality, Deliver Results.
    *   **Typical Role Expectations:** Ability to operate at scale, operational excellence, high standards, handling high ambiguity.
    *   **Keywords:** AWS, Scalability, DynamoDB, EC2, Lambda, Leadership Principles, Bar Raiser, Operational Excellence, Customer Obsession.
    """,
    "Microsoft": """
    **Company Analysis: Microsoft**
    *   **Tone:** Collaborative, growth-oriented, empathetic, professional.
    *   **Hiring Culture:** Strong emphasis on "Growth Mindset" (learn-it-all vs. know-it-all). Values diversity and inclusion.
    *   **Preferred Communication Style:** Collaborative, respectful, clear, and inclusive.
    *   **Expected Values:** Respect, Integrity, Accountability, Growth Mindset, One Microsoft.
    *   **Typical Role Expectations:** Enterprise-grade development, collaboration across teams, understanding of the Microsoft ecosystem (Azure, .NET).
    *   **Keywords:** Azure, .NET, C#, Cloud Computing, Enterprise, Growth Mindset, Copilot, AI, Inclusive Design.
    """,
    "Meta": """
    **Company Analysis: Meta (Facebook)**
    *   **Tone:** Fast-paced, bold, hacker-centric, impact-driven.
    *   **Hiring Culture:** "Move Fast", "Build Awesome Things". Focus on coding speed and correctness (Jedi/Ninja coding interviews).
    *   **Preferred Communication Style:** Direct, open, informal, feedback-heavy.
    *   **Expected Values:** Move Fast, Focus on Impact, Be Open, Live in the Future.
    *   **Typical Role Expectations:** Full-stack capability, ability to ship code quickly, product sense.
    *   **Keywords:** React, GraphQL, Hack (PHP), Social Graph, PyTorch, Metaverse, AI, Hackathon, Move Fast.
    """,
    "Netflix": """
    **Company Analysis: Netflix**
    *   **Tone:** Candid, mature, high-performance, "No Rules Rules".
    *   **Hiring Culture:** "Stunning Colleagues" only. Highly competitive. Values "Context, not Control".
    *   **Preferred Communication Style:** Radical candor, extremely open and honest feedback.
    *   **Expected Values:** Judgment, Communication, Impact, Curiosity, Innovation, Courage, Passion, Selflessness, Inclusion, Integrity.
    *   **Typical Role Expectations:** Senior-level autonomy, full ownership of the stack, decision-making ability.
    *   **Keywords:** Streaming, Microservices, Chaos Engineering, AWS, Java, Spring Boot, Freedom and Responsibility, Context not Control.
    """,
    "Tesla": """
    **Company Analysis: Tesla**
    *   **Tone:** Intense, urgent, mission-driven, first-principles thinking.
    *   **Hiring Culture:** Hardcore, all-in, solving impossible problems.
    *   **Preferred Communication Style:** Direct, efficient, no fluff.
    *   **Expected Values:** Accelerating the world's transition to sustainable energy. First Principles thinking.
    *   **Typical Role Expectations:** Hands-on engineering, long hours, rapid iteration, manufacturing excellence.
    *   **Keywords:** Autonomy, EV, Battery Tech, Manufacturing, Robotics, C++, Python, First Principles, Hardcore.
    """,
    "Apple": """
    **Company Analysis: Apple**
    *   **Tone:** Perfectionist, secretive, design-led, polished.
    *   **Hiring Culture:** Focus on deep specialization, craftsmanship, and cultural fit.
    *   **Preferred Communication Style:** Precise, deliberate, guarded (secrecy is paramount).
    *   **Expected Values:** Think Different, Perfection, Simplicity, Privacy is a fundamental human right.
    *   **Typical Role Expectations:** Deep domain expertise, attention to detail, user-centric design.
    *   **Keywords:** iOS, Swift, Objective-C, Cocoa Touch, Human Interface Guidelines, Privacy, Hardware-Software Integration.
    """,
    "Nvidia": """
    **Company Analysis: Nvidia**
    *   **Tone:** Cutting-edge, intellectual, speed-oriented.
    *   **Hiring Culture:** Focus on "Speed of Light" execution, intellectual honesty.
    *   **Preferred Communication Style:** Technical, precise, forward-looking.
    *   **Expected Values:** Innovation, Intellectual Honesty, Speed, Agility, One Team.
    *   **Typical Role Expectations:** High-performance computing, hardware-software co-design, AI/Deep Learning expertise.
    *   **Keywords:** GPU, CUDA, Deep Learning, AI, Ray Tracing, HPC, C++, Python, Omniverse.
    """,
    "Adobe": """
    **Company Analysis: Adobe**
    *   **Tone:** Creative, genuine, innovative, exceptional.
    *   **Hiring Culture:** Values creativity and community. "Adobe for All".
    *   **Preferred Communication Style:** Visual, storytelling, collaborative.
    *   **Expected Values:** Genuine, Exceptional, Innovative, Involved.
    *   **Typical Role Expectations:** Passion for digital experiences, cloud services, and creative tools.
    *   **Keywords:** Creative Cloud, Experience Cloud, Photoshop, PDF, SaaS, AI (Sensei), Design.
    """,
    "Uber": """
    **Company Analysis: Uber**
    *   **Tone:** Hustle, gritty, go-getter, data-driven.
    *   **Hiring Culture:** "Go get it" attitude. Focus on execution and scale.
    *   **Preferred Communication Style:** Direct, data-backed.
    *   **Expected Values:** Go Get It, Trip Obsessed, Build with Heart, Stand for what's right.
    *   **Typical Role Expectations:** Handling massive scale, real-time data, marketplace dynamics.
    *   **Keywords:** Marketplace, Real-time, Logistics, Go, Python, Microservices, Mobile, Algorithms.
    """,
    "Salesforce": """
    **Company Analysis: Salesforce**
    *   **Tone:** "Ohana" (Family), trust-centric, philanthropic.
    *   **Hiring Culture:** Focus on cultural fit, trust, and customer success.
    *   **Preferred Communication Style:** Friendly, customer-centric, inclusive.
    *   **Expected Values:** Trust, Customer Success, Innovation, Equality, Sustainability.
    *   **Typical Role Expectations:** CRM expertise, cloud platform development, enterprise solutions.
    *   **Keywords:** CRM, Apex, Visualforce, Lightning, SaaS, Cloud, Trust, Ohana.
    """,
    "Oracle": """
    **Company Analysis: Oracle**
    *   **Tone:** Corporate, aggressive, results-oriented, competitive.
    *   **Hiring Culture:** Focus on sales drive and engineering robustness.
    *   **Preferred Communication Style:** Professional, business-focused.
    *   **Expected Values:** Integrity, Mutual Respect, Teamwork, Communication, Innovation.
    *   **Typical Role Expectations:** Database internals, cloud infrastructure, enterprise Java.
    *   **Keywords:** Database, SQL, Java, OCI (Oracle Cloud Infrastructure), ERP, Enterprise.
    """,
    "TCS": """
    **Company Analysis: TCS (Tata Consultancy Services)**
    *   **Tone:** Professional, process-oriented, reliable.
    *   **Hiring Culture:** Mass hiring, focus on trainability and adaptability.
    *   **Preferred Communication Style:** Formal, hierarchical, client-centric.
    *   **Expected Values:** Leading Change, Integrity, Respect for Individual, Excellence, Learning and Sharing.
    *   **Typical Role Expectations:** Service delivery, adherence to processes, flexibility in technology.
    *   **Keywords:** IT Services, Digital Transformation, Agile, SDLC, Client Management, Tata.
    """,
    "Infosys": """
    **Company Analysis: Infosys**
    *   **Tone:** Learning-oriented, professional, "Navigate your next".
    *   **Hiring Culture:** Strong focus on training (Mysore campus), learnability.
    *   **Preferred Communication Style:** Professional, structured.
    *   **Expected Values:** Client Value, Leadership by Example, Integrity and Transparency, Fairness, Excellence.
    *   **Typical Role Expectations:** Software development lifecycle, maintenance, testing, consulting.
    *   **Keywords:** IT Services, Consulting, NextGen, AI, Automation, Agile.
    """,
    "Wipro": """
    **Company Analysis: Wipro**
    *   **Tone:** Resilient, spirit of Wipro, client-focused.
    *   **Hiring Culture:** Values dedication and adaptability.
    *   **Preferred Communication Style:** Professional, respectful.
    *   **Expected Values:** Spirit of Wipro (Intensity to Win, Act with Sensitivity, Unyielding Integrity).
    *   **Typical Role Expectations:** Delivery excellence, technology consulting.
    *   **Keywords:** IT Consulting, Business Process Services, Digital, Cloud, Cyber Security.
    """,
    "Deloitte": """
    **Company Analysis: Deloitte**
    *   **Tone:** Professional, expert, polished, "Green Dot".
    *   **Hiring Culture:** High achievers, networking ability, versatility.
    *   **Preferred Communication Style:** Professional, articulate, consultative.
    *   **Expected Values:** Integrity, Outstanding value to markets and clients, Commitment to each other, Strength from cultural diversity.
    *   **Typical Role Expectations:** Consulting, strategy, implementation, auditing, risk advisory.
    *   **Keywords:** Consulting, Audit, Tax, Advisory, Strategy, Big 4, Transformation.
    """,
    "Accenture": """
    **Company Analysis: Accenture**
    *   **Tone:** Innovation-led, professional, high-performance.
    *   **Hiring Culture:** "High performance. Delivered." Focus on continuous learning.
    *   **Preferred Communication Style:** Professional, jargon-heavy (consulting speak), structured.
    *   **Expected Values:** Client Value Creation, One Global Network, Respect for the Individual, Best People, Integrity, Stewardship.
    *   **Typical Role Expectations:** Technology implementation, digital transformation, consulting.
    *   **Keywords:** Strategy, Consulting, Digital, Technology, Operations, Innovation, Cloud.
    """,
    "IBM": """
    **Company Analysis: IBM**
    *   **Tone:** Formal, research-oriented, enterprise-focused, "Think".
    *   **Hiring Culture:** Values deep technical expertise, academic background, and stability.
    *   **Preferred Communication Style:** Structured, professional, precise.
    *   **Expected Values:** Dedication to every client's success, Innovation that matters, Trust and personal responsibility.
    *   **Typical Role Expectations:** Enterprise software development, cloud computing, AI research, legacy system maintenance.
    *   **Keywords:** Hybrid Cloud, AI (Watson), Red Hat, Quantum Computing, Enterprise, Mainframe, Consulting.
    """,
    "Cisco": """
    **Company Analysis: Cisco**
    *   **Tone:** Professional, customer-centric, secure, connected.
    *   **Hiring Culture:** Focus on networking expertise, certifications (CCNA/CCIE), and security.
    *   **Preferred Communication Style:** Clear, technical, solution-oriented.
    *   **Expected Values:** Connect everything, Innovate everywhere, Benefit everyone.
    *   **Typical Role Expectations:** Network engineering, security, IoT, software-defined networking.
    *   **Keywords:** Networking, Security, IoT, Webex, SD-WAN, Cloud, CCNA.
    """,
    "SAP": """
    **Company Analysis: SAP**
    *   **Tone:** Corporate, process-driven, efficient, global.
    *   **Hiring Culture:** Values domain knowledge (ERP, Supply Chain), German engineering precision.
    *   **Preferred Communication Style:** Formal, detailed, process-oriented.
    *   **Expected Values:** "Run Simple", Customer Success, Innovation.
    *   **Typical Role Expectations:** ERP development, ABAP, cloud migration, enterprise solutions.
    *   **Keywords:** ERP, HANA, ABAP, Cloud, Enterprise, Supply Chain, Business Technology Platform.
    """,
    "Intel": """
    **Company Analysis: Intel**
    *   **Tone:** Technical, precision-oriented, hardware-focused.
    *   **Hiring Culture:** "Moore's Law", engineering excellence, deep technical knowledge.
    *   **Preferred Communication Style:** Data-driven, precise, technical.
    *   **Expected Values:** Customer First, Fearless Innovation, Results Driven, One Intel.
    *   **Typical Role Expectations:** Semiconductor design, driver development, low-level programming.
    *   **Keywords:** Semiconductors, x86, Processors, IoT, Edge Computing, C/C++, Hardware.
    """,
    "AMD": """
    **Company Analysis: AMD**
    *   **Tone:** Competitive, high-performance, resilient.
    *   **Hiring Culture:** Underdog spirit, pushing boundaries in HPC and gaming.
    *   **Preferred Communication Style:** Direct, performance-focused.
    *   **Expected Values:** High Performance culture, Innovation, Execution.
    *   **Typical Role Expectations:** GPU/CPU architecture, high-performance computing, driver optimization.
    *   **Keywords:** Ryzen, Radeon, HPC, GPU, CPU, Semiconductor, Gaming.
    """,
    "Qualcomm": """
    **Company Analysis: Qualcomm**
    *   **Tone:** Innovative, IP-focused, wireless-centric.
    *   **Hiring Culture:** Strong focus on patents, R&D, and telecommunications standards.
    *   **Preferred Communication Style:** Technical, standard-compliant, detailed.
    *   **Expected Values:** Innovation, Execution, Partnership.
    *   **Typical Role Expectations:** Embedded systems, wireless protocols (5G/6G), SoC design.
    *   **Keywords:** 5G, Snapdragon, Wireless, Embedded Systems, SoC, Mobile, IoT.
    """,
    "Twitter": """
    **Company Analysis: Twitter (X)**
    *   **Tone:** Fast, intense, "Hardcore", direct.
    *   **Hiring Culture:** Extreme ownership, high output, lean teams.
    *   **Preferred Communication Style:** Concise, direct, "truth-seeking".
    *   **Expected Values:** Free speech, transparency, speed, intensity.
    *   **Typical Role Expectations:** Full-stack capability, handling massive scale, rapid iteration.
    *   **Keywords:** Real-time, Scala, Distributed Systems, Social Media, High Scale, Recommendation Algorithms.
    """,
    "LinkedIn": """
    **Company Analysis: LinkedIn**
    *   **Tone:** Professional, community-focused, "Economic Graph".
    *   **Hiring Culture:** Values craftsmanship, "Members First", and collaboration.
    *   **Preferred Communication Style:** Professional, inclusive, thoughtful.
    *   **Expected Values:** Members First, Relationships Matter, Be Open, Honest and Constructive.
    *   **Typical Role Expectations:** High-quality engineering, data privacy, social graph analysis.
    *   **Keywords:** Social Graph, Economic Graph, Big Data, Kafka, AI/ML, Professional Networking.
    """,
    "Airbnb": """
    **Company Analysis: Airbnb**
    *   **Tone:** Design-led, empathetic, "Belong Anywhere".
    *   **Hiring Culture:** "Core Values" interview is critical. Focus on design and host empathy.
    *   **Preferred Communication Style:** Storytelling, visual, empathetic.
    *   **Expected Values:** Champion the Mission, Be a Host, Embrace the Adventure, Be a Cereal Entrepreneur.
    *   **Typical Role Expectations:** Product-focused engineering, beautiful UI/UX, marketplace dynamics.
    *   **Keywords:** Marketplace, Travel, Design System, React, Service-Oriented Architecture, Hospitality.
    """,
    "Stripe": """
    **Company Analysis: Stripe**
    *   **Tone:** Developer-centric, precise, written-culture, "Increase the GDP of the internet".
    *   **Hiring Culture:** Writing heavy, "lurker" culture (transparency), high standards for documentation.
    *   **Preferred Communication Style:** Excellent written communication, clear, concise.
    *   **Expected Values:** Users First, Move with Urgency, Think Rigorously, Trust and be Trustworthy.
    *   **Typical Role Expectations:** API design, financial infrastructure, reliability, developer experience.
    *   **Keywords:** FinTech, API, Payments, Ruby, Infrastructure, Developer Tools, Global Economy.
    """,
    "OpenAI": """
    **Company Analysis: OpenAI**
    *   **Tone:** Mission-driven, safety-conscious, research-heavy, "AGI".
    *   **Hiring Culture:** World-class researchers and engineers, focus on AI safety and alignment.
    *   **Preferred Communication Style:** Academic, precise, thoughtful about long-term impact.
    *   **Expected Values:** AGI for the benefit of all, Safety, Technical Leadership.
    *   **Typical Role Expectations:** Large Language Models, reinforcement learning, supercomputing infrastructure.
    *   **Keywords:** AGI, LLM, GPT, Reinforcement Learning, AI Safety, PyTorch, Research.
    """,
    "DeepMind": """
    **Company Analysis: Google DeepMind**
    *   **Tone:** Academic, rigorous, scientific, "Solving Intelligence".
    *   **Hiring Culture:** PhD-heavy, publication-focused, solving fundamental problems.
    *   **Preferred Communication Style:** Scientific, data-backed, peer-reviewed style.
    *   **Expected Values:** Scientific Rigor, Ethical AI, Collaboration.
    *   **Typical Role Expectations:** Fundamental AI research, neuroscience-inspired AI, AlphaFold.
    *   **Keywords:** Reinforcement Learning, Neuroscience, AlphaGo, Research, TensorFlow/JAX, AGI.
    """,
    "Snowflake": """
    **Company Analysis: Snowflake**
    *   **Tone:** Data-driven, cloud-native, scalable.
    *   **Hiring Culture:** Focus on database internals, distributed systems, and cloud infrastructure.
    *   **Preferred Communication Style:** Technical, performance-oriented.
    *   **Expected Values:** Put Customers First, Integrity Always, Think Big, Be Excellent.
    *   **Typical Role Expectations:** Building data warehouse engine, cloud storage optimization.
    *   **Keywords:** Data Warehousing, Cloud, SQL, Distributed Systems, SaaS, Data Lake.
    """,
    "Databricks": """
    **Company Analysis: Databricks**
    *   **Tone:** Open source, data + AI, "Lakehouse".
    *   **Hiring Culture:** Strong academic roots (Spark creators), values open source contributions.
    *   **Preferred Communication Style:** Technical, community-focused.
    *   **Expected Values:** Customer Obsession, First Principles, Teamwork.
    *   **Typical Role Expectations:** Big data processing, machine learning infrastructure, Spark optimization.
    *   **Keywords:** Spark, Lakehouse, Delta Lake, Big Data, AI, Scala, Open Source.
    """,
    "Atlassian": """
    **Company Analysis: Atlassian**
    *   **Tone:** Collaborative, open, "Don't #@!% the customer".
    *   **Hiring Culture:** Values teamwork and "Open Company, No Bullshit".
    *   **Preferred Communication Style:** Open, honest, informal but professional.
    *   **Expected Values:** Open Company, Build with Heart and Balance, Play, as a Team.
    *   **Typical Role Expectations:** SaaS development, collaboration tools, cloud migration.
    *   **Keywords:** Jira, Confluence, SaaS, Collaboration, Agile, Cloud.
    """,
    "Palantir": """
    **Company Analysis: Palantir**
    *   **Tone:** Mission-driven, secretive, intense, "Save the Shire".
    *   **Hiring Culture:** Values "Forward Deployed Engineers", solving critical problems for governments/enterprises.
    *   **Preferred Communication Style:** Direct, problem-solving focused.
    *   **Expected Values:** Mission First, Operational Excellence.
    *   **Typical Role Expectations:** Data integration, large-scale analytics, field engineering.
    *   **Keywords:** Big Data, Analytics, Gotham, Foundry, Forward Deployed Engineer, Java, TypeScript.
    """,
    "DoorDash": """
    **Company Analysis: DoorDash**
    *   **Tone:** Operational, fast, logistics-focused.
    *   **Hiring Culture:** "1% Better Every Day", values bias for action.
    *   **Preferred Communication Style:** Data-driven, execution-focused.
    *   **Expected Values:** Be an Owner, Dream Big and Start Small, We are One Team.
    *   **Typical Role Expectations:** Marketplace algorithms, logistics optimization, mobile app dev.
    *   **Keywords:** Logistics, Marketplace, Last-Mile Delivery, Mobile, Real-time Systems.
    """,
    "Rivian": """
    **Company Analysis: Rivian**
    *   **Tone:** Adventurous, sustainable, hardware+software.
    *   **Hiring Culture:** Passion for outdoors and sustainability.
    *   **Preferred Communication Style:** Collaborative, mission-aligned.
    *   **Expected Values:** Keep the World Adventurous Forever.
    *   **Typical Role Expectations:** EV software, autonomy, battery management systems.
    *   **Keywords:** EV, Automotive, Sustainability, Adventure, IoT, Embedded.
    """,
    "SpaceX": """
    **Company Analysis: SpaceX**
    *   **Tone:** Audacious, hardcore, "Multi-planetary".
    *   **Hiring Culture:** Extremely high bar, long hours, passion for space is mandatory.
    *   **Preferred Communication Style:** First principles, extremely direct, no jargon.
    *   **Expected Values:** Making Humanity Multi-Planetary, Extreme Ownership.
    *   **Typical Role Expectations:** Avionics, flight software, propulsion, manufacturing engineering.
    *   **Keywords:** Aerospace, Rockets, Starship, C++, Real-time Systems, First Principles.
    """,
    "Robinhood": """
    **Company Analysis: Robinhood**
    *   **Tone:** Democratizing finance, sleek, mobile-first.
    *   **Hiring Culture:** FinTech regulation awareness + consumer tech speed.
    *   **Preferred Communication Style:** Clear, compliant but accessible.
    *   **Expected Values:** Safety First, Participation is Power, Radical Customer Focus.
    *   **Typical Role Expectations:** High-frequency trading systems, mobile security, crypto.
    *   **Keywords:** FinTech, Trading, Mobile, Security, Crypto, Democratize Finance.
    """,
    "Shopify": """
    **Company Analysis: Shopify**
    *   **Tone:** Entrepreneurial, "Arm the rebels", remote-first.
    *   **Hiring Culture:** Values "Digital by Design", commerce expertise.
    *   **Preferred Communication Style:** Asynchronous, written, thoughtful.
    *   **Expected Values:** Merchant Obsession, Thrive on Change, Be Constant Learners.
    *   **Typical Role Expectations:** E-commerce platform, Ruby on Rails, React, developer tools.
    *   **Keywords:** E-commerce, Ruby on Rails, React, Remote, Entrepreneurship.
    """,
    "EY": """
    **Company Analysis: EY (Ernst & Young)**
    *   **Tone:** Professional, consultative, "Building a better working world".
    *   **Hiring Culture:** Professional services, audit/tax/consulting mix.
    *   **Preferred Communication Style:** Formal, client-ready, structured.
    *   **Expected Values:** Integrity, Respect, Teaming.
    *   **Typical Role Expectations:** Technology consulting, digital transformation, risk assurance.
    *   **Keywords:** Consulting, Assurance, Tax, Strategy, Digital Transformation, Big 4.
    """,
    "PwC": """
    **Company Analysis: PwC**
    *   **Tone:** Trusted, solving important problems.
    *   **Hiring Culture:** High integrity, business acumen.
    *   **Preferred Communication Style:** Professional, insightful.
    *   **Expected Values:** Act with Integrity, Make a Difference, Care, Work Together, Reimagine the Possible.
    *   **Typical Role Expectations:** Management consulting, cybersecurity, data analytics.
    *   **Keywords:** Consulting, Audit, Advisory, Trust, Solutions, Big 4.
    """,
    "KPMG": """
    **Company Analysis: KPMG**
    *   **Tone:** Reliable, compliance-focused, professional.
    *   **Hiring Culture:** Values quality and integrity.
    *   **Preferred Communication Style:** Formal, precise.
    *   **Expected Values:** Integrity, Excellence, Courage, Together, For Better.
    *   **Typical Role Expectations:** Risk consulting, deal advisory, technology implementation.
    *   **Keywords:** Audit, Tax, Advisory, Compliance, Risk, Big 4.
    """,
    "Capgemini": """
    **Company Analysis: Capgemini**
    *   **Tone:** Multicultural, technology-driven, "Get the Future You Want".
    *   **Hiring Culture:** Values diversity and digital inclusion.
    *   **Preferred Communication Style:** Collaborative, professional.
    *   **Expected Values:** Honesty, Boldness, Trust, Freedom, Fun, Modesty, Team Spirit.
    *   **Typical Role Expectations:** IT services, cloud services, digital engineering.
    *   **Keywords:** Consulting, Digital Transformation, Cloud, Engineering, AI.
    """,
    "Cognizant": """
    **Company Analysis: Cognizant**
    *   **Tone:** Practical, delivery-focused, "Intuition engineered".
    *   **Hiring Culture:** Large-scale recruitment, focus on digital skills.
    *   **Preferred Communication Style:** Professional, process-oriented.
    *   **Expected Values:** Customer Focus, Passion, Collaboration, Integrity, Transparency.
    *   **Typical Role Expectations:** Application development, maintenance, BPO, digital solutions.
    *   **Keywords:** IT Services, Digital, Healthcare IT, Outsourcing, Cloud.
    """,
    "Tech Mahindra": """
    **Company Analysis: Tech Mahindra**
    *   **Tone:** Connected, "NXT.NOW".
    *   **Hiring Culture:** Strong telecom roots, focus on 5G and connectivity.
    *   **Preferred Communication Style:** Professional, client-focused.
    *   **Expected Values:** Openness, Freedom to Explore, Customer First.
    *   **Typical Role Expectations:** Telecom software, network services, customer experience.
    *   **Keywords:** Telecom, 5G, IT Services, Connectivity, Digital.
    """,
    "Sony": """
    **Company Analysis: Sony**
    *   **Tone:** Creative, entertainment-focused, "Kando" (Emotion).
    *   **Hiring Culture:** Blend of hardware excellence and creative content.
    *   **Preferred Communication Style:** Respectful, innovative.
    *   **Expected Values:** Dreams & Curiosity, Diversity, Integrity & Sincerity, Sustainability.
    *   **Typical Role Expectations:** Embedded software, image processing, game development (PlayStation).
    *   **Keywords:** PlayStation, Imaging, Entertainment, Hardware, AI, Robotics.
    """,
    "Samsung": """
    **Company Analysis: Samsung**
    *   **Tone:** Formal, ambitious, hardware-dominant.
    *   **Hiring Culture:** Competitive, hierarchical (Korean corporate culture influence), intense.
    *   **Preferred Communication Style:** Formal, hierarchical, respectful.
    *   **Expected Values:** People, Excellence, Change, Integrity, Co-prosperity.
    *   **Typical Role Expectations:** Mobile development, semiconductor R&D, display technology.
    *   **Keywords:** Android, Semiconductor, Hardware, Mobile, IoT, 5G.
    """,
    "EA": """
    **Company Analysis: EA (Electronic Arts)**
    *   **Tone:** Creative, "Inspire the World to Play".
    *   **Hiring Culture:** Passion for games, blend of art and tech.
    *   **Preferred Communication Style:** Creative, collaborative.
    *   **Expected Values:** Creativity, Passion, Determination, Learning, Teamwork.
    *   **Typical Role Expectations:** Game engine programming, graphics rendering, gameplay logic.
    *   **Keywords:** Gaming, Frostbite, Sports, C++, Graphics, Interactive Entertainment.
    """,
    "Epic Games": """
    **Company Analysis: Epic Games**
    *   **Tone:** High-performance, engine-focused, "Unreal".
    *   **Hiring Culture:** Very high technical bar (C++), metaverse vision.
    *   **Preferred Communication Style:** Technical, direct.
    *   **Expected Values:** Be Epic, Do the Right Thing.
    *   **Typical Role Expectations:** Engine development, tools programming, backend for massive scale (Fortnite).
    *   **Keywords:** Unreal Engine, Fortnite, C++, Metaverse, Graphics, Real-time 3D.
    """,
    "Unity": """
    **Company Analysis: Unity**
    *   **Tone:** Creator-focused, "The world is a better place with more creators".
    *   **Hiring Culture:** Values tool-building for others.
    *   **Preferred Communication Style:** Empathetic, technical.
    *   **Expected Values:** Users First, Best Ideas Win, In It Together, Go Bold.
    *   **Typical Role Expectations:** Engine tools, C# scripting, graphics optimization, ad-tech.
    *   **Keywords:** Game Engine, C#, 3D, AR/VR, Real-time, Creator Tools.
    """,
    "Flipkart": """
    **Company Analysis: Flipkart**
    *   **Tone:** Fast, "India-first", e-commerce giant.
    *   **Hiring Culture:** Bias for action, problem solving for Indian context.
    *   **Preferred Communication Style:** Data-driven, customer-centric.
    *   **Expected Values:** Audacity, Bias for Action, Customer First, Integrity, Inclusion.
    *   **Typical Role Expectations:** Supply chain tech, high-scale e-commerce, mobile app.
    *   **Keywords:** E-commerce, Logistics, India, Scale, Mobile, Supply Chain.
    """,
    "Swiggy": """
    **Company Analysis: Swiggy**
    *   **Tone:** Hyper-local, convenience, fast.
    *   **Hiring Culture:** Values speed and logistics optimization.
    *   **Preferred Communication Style:** Fast, efficient.
    *   **Expected Values:** Consumer Comes First, Act Like an Owner.
    *   **Typical Role Expectations:** Logistics algorithms, real-time tracking, high-concurrency backend.
    *   **Keywords:** Food Delivery, Hyper-local, Logistics, Real-time, Quick Commerce.
    """,
    "Zomato": """
    **Company Analysis: Zomato**
    *   **Tone:** Foodie, humorous, resilient.
    *   **Hiring Culture:** "Better food for more people".
    *   **Preferred Communication Style:** Informal, direct, passionate.
    *   **Expected Values:** Resilience, Ownership, Customer Focus.
    *   **Typical Role Expectations:** Search algorithms, recommendation systems, operations tech.
    *   **Keywords:** Food Tech, Discovery, Delivery, Marketplace, IPO.
    """,
    "Paytm": """
    **Company Analysis: Paytm**
    *   **Tone:** FinTech, aggressive, ubiquitous.
    *   **Hiring Culture:** Fast-paced, payments-focused.
    *   **Preferred Communication Style:** Business-focused, execution-oriented.
    *   **Expected Values:** Speed, Reliability, Innovation.
    *   **Typical Role Expectations:** Payments gateway, wallet tech, financial compliance.
    *   **Keywords:** FinTech, Payments, UPI, Wallet, Digital India.
    """,
    "Byju's": """
    **Company Analysis: Byju's**
    *   **Tone:** Educational, aggressive growth, sales-driven.
    *   **Hiring Culture:** High energy, focus on ed-tech scale.
    *   **Preferred Communication Style:** Persuasive, goal-oriented.
    *   **Expected Values:** Impact, Speed.
    *   **Typical Role Expectations:** Content delivery platforms, gamification, mobile learning apps.
    *   **Keywords:** EdTech, Learning App, Gamification, Sales, Growth.
    """,
    "Bloomberg": """
    **Company Analysis: Bloomberg**
    *   **Tone:** Fast, financial, data-centric, authoritative.
    *   **Hiring Culture:** Values deep C++ expertise, problem-solving, and philanthropy.
    *   **Preferred Communication Style:** Direct, factual, efficient.
    *   **Expected Values:** Innovation, Collaboration, Doing the Right Thing, Philanthropy.
    *   **Typical Role Expectations:** Low-latency systems, financial data processing, terminal software.
    *   **Keywords:** C++, Financial Data, Low Latency, Distributed Systems, Terminal.
    """,
    "Goldman Sachs": """
    **Company Analysis: Goldman Sachs**
    *   **Tone:** Elite, high-pressure, commercial, professional.
    *   **Hiring Culture:** "Engineering at the center of the business". High standard for algorithms.
    *   **Preferred Communication Style:** Professional, concise, commercial.
    *   **Expected Values:** Client Service, Excellence, Integrity, Partnership.
    *   **Typical Role Expectations:** Proprietary platforms (Slang/SecDB), risk systems, trading platforms.
    *   **Keywords:** FinTech, Trading, Risk Management, Java, C++, Slang, Investment Banking.
    """,
    "JPMorgan Chase": """
    **Company Analysis: JPMorgan Chase (JPMC)**
    *   **Tone:** Massive, stable, modernizing.
    *   **Hiring Culture:** Huge scale hiring, focus on modernizing legacy banking tech.
    *   **Preferred Communication Style:** Professional, structured.
    *   **Expected Values:** Service, Heart, Curiosity, Courage.
    *   **Typical Role Expectations:** Enterprise Java/Python, cloud migration, cybersecurity.
    *   **Keywords:** Banking, FinTech, Cloud, Cybersecurity, Java, Python, Scale.
    """,
    "Morgan Stanley": """
    **Company Analysis: Morgan Stanley**
    *   **Tone:** Prestigious, client-focused, technological.
    *   **Hiring Culture:** Values technologists who understand finance.
    *   **Preferred Communication Style:** Professional, articulate.
    *   **Expected Values:** Do the Right Thing, Put Clients First, Lead with Exceptional Ideas.
    *   **Typical Role Expectations:** Wealth management systems, algorithmic trading, enterprise infrastructure.
    *   **Keywords:** Wealth Management, Institutional Securities, Java, C++, Scala, FinTech.
    """,
    "Spotify": """
    **Company Analysis: Spotify**
    *   **Tone:** Cool, agile, music-loving, "Band members".
    *   **Hiring Culture:** Famous for "Spotify Model" (Squads, Tribes). Values autonomy.
    *   **Preferred Communication Style:** Informal, passionate, collaborative.
    *   **Expected Values:** Innovative, Collaborative, Sincere, Passionate, Playful.
    *   **Typical Role Expectations:** Backend scaling, recommendation engines, mobile app polish.
    *   **Keywords:** Audio Streaming, Personalization, Squads, Java, Python, Mobile, ML.
    """,
    "Reddit": """
    **Company Analysis: Reddit**
    *   **Tone:** Community-focused, "Front page of the internet", quirky.
    *   **Hiring Culture:** Values understanding internet culture and community safety.
    *   **Preferred Communication Style:** Authentic, direct, "human".
    *   **Expected Values:** Remember the Human, Evolve, Default Open.
    *   **Typical Role Expectations:** Scaling high-traffic feeds, ad-tech, moderation tools.
    *   **Keywords:** Community, Social Media, Python, Go, GraphQL, Ads, Scale.
    """,
    "Dropbox": """
    **Company Analysis: Dropbox**
    *   **Tone:** Smart, simple, "Virtual First" (Remote).
    *   **Hiring Culture:** High engineering bar, values "enlightened" working style.
    *   **Preferred Communication Style:** Thoughtful, written, asynchronous.
    *   **Expected Values:** Be Worthy of Trust, Sweat the Details, Aim Higher.
    *   **Typical Role Expectations:** Sync engines, file systems, distributed storage.
    *   **Keywords:** Cloud Storage, Sync, Distributed Systems, Python, Go, Rust, Remote.
    """,
    "Slack": """
    **Company Analysis: Slack**
    *   **Tone:** Playful, empathetic, polished, "Pleasant".
    *   **Hiring Culture:** Strong focus on craftsmanship and empathy for the user.
    *   **Preferred Communication Style:** Clear, concise, human, emoji-friendly.
    *   **Expected Values:** Empathy, Courtesy, Thriving, Craftsmanship, Playfulness, Solidarity.
    *   **Typical Role Expectations:** Real-time messaging, intuitive UI, platform integrations.
    *   **Keywords:** Collaboration, Messaging, Real-time, PHP/Hack, Frontend, UX.
    """,
    "GitHub": """
    **Company Analysis: GitHub**
    *   **Tone:** Developer-first, open source, "Social Coding".
    *   **Hiring Culture:** Remote-first pioneers. Values open source contributions.
    *   **Preferred Communication Style:** Asynchronous, markdown-heavy, collaborative.
    *   **Expected Values:** Customer Obsession, Ship to Learn, Growth Mindset.
    *   **Typical Role Expectations:** Git internals, developer tools, CI/CD (Actions).
    *   **Keywords:** Git, DevOps, Open Source, Ruby on Rails, Go, Remote, Developer Tools.
    """,
    "Pinterest": """
    **Company Analysis: Pinterest**
    *   **Tone:** Visual, positive, inspirational.
    *   **Hiring Culture:** "Knitting" (Collaboration). Values diversity and inspiration.
    *   **Preferred Communication Style:** Visual, positive, collaborative.
    *   **Expected Values:** Put Pinners First, Knit Connecitons, Be an Owner.
    *   **Typical Role Expectations:** Computer vision, recommendation systems, mobile.
    *   **Keywords:** Visual Discovery, Computer Vision, ML, Python, Java, Mobile.
    """,
    "TikTok": """
    **Company Analysis: TikTok (ByteDance)**
    *   **Tone:** Hyper-growth, intense, algorithmic, "Always Day 1".
    *   **Hiring Culture:** Values speed, data-driven decisions, and high output.
    *   **Preferred Communication Style:** Direct, data-backed, efficient.
    *   **Expected Values:** Aim for the Highest, Be Grounded and Courageous, Be Open and Humble.
    *   **Typical Role Expectations:** Recommendation algorithms, high-concurrency systems, mobile video.
    *   **Keywords:** Short Video, Recommendation Systems, AI, Go, Python, Mobile, Scale.
    """,
    "Alibaba": """
    **Company Analysis: Alibaba**
    *   **Tone:** Massive, ecosystem-driven, "To make it easy to do business anywhere".
    *   **Hiring Culture:** Values dedication and customer success.
    *   **Preferred Communication Style:** Business-focused, respectful.
    *   **Expected Values:** Customers First, Teamwork, Embrace Change, Integrity, Passion, Commitment.
    *   **Typical Role Expectations:** E-commerce scale, cloud infrastructure, payments.
    *   **Keywords:** E-commerce, Cloud, Java, Distributed Systems, High Concurrency.
    """,
    "Tencent": """
    **Company Analysis: Tencent**
    *   **Tone:** Social, gaming, innovative, "Value for Users".
    *   **Hiring Culture:** Competitive, product-focused.
    *   **Preferred Communication Style:** Professional, efficient.
    *   **Expected Values:** Integrity, Proactivity, Collaboration, Creativity.
    *   **Typical Role Expectations:** Game development, social platforms (WeChat), cloud.
    *   **Keywords:** Gaming, WeChat, Social, Cloud, AI, C++.
    """,
    "Baidu": """
    **Company Analysis: Baidu**
    *   **Tone:** Technical, AI-first.
    *   **Hiring Culture:** "Simple and Reliable". Engineering driven.
    *   **Preferred Communication Style:** Technical, data-driven.
    *   **Expected Values:** Simple and Reliable.
    *   **Typical Role Expectations:** Search engines, autonomous driving, deep learning.
    *   **Keywords:** Search, AI, Deep Learning, Autonomous Driving, C++.
    """,
    "SAP Labs India": """
    **Company Analysis: SAP Labs India**
    *   **Tone:** Innovation within enterprise, "Silicon Valley of India".
    *   **Hiring Culture:** Strong focus on R&D and product ownership from India.
    *   **Preferred Communication Style:** Professional, collaborative.
    *   **Expected Values:** Innovation, Customer Success, Diversity.
    *   **Typical Role Expectations:** Cloud ERP, HANA, Business Technology Platform.
    *   **Keywords:** ERP, Cloud, HANA, Java, ABAP, Innovation.
    """,
    "Siemens": """
    **Company Analysis: Siemens**
    *   **Tone:** Industrial, reliable, engineering-heavy.
    *   **Hiring Culture:** Values longevity, domain expertise, and precision.
    *   **Preferred Communication Style:** Formal, technical.
    *   **Expected Values:** Responsible, Excellent, Innovative.
    *   **Typical Role Expectations:** Industrial automation, healthcare imaging, embedded systems.
    *   **Keywords:** Industrial Automation, IoT, Healthcare, Embedded Systems, C++, Engineering.
    """,
    "Philips": """
    **Company Analysis: Philips**
    *   **Tone:** Health-focused, innovative, "Innovation and you".
    *   **Hiring Culture:** Values improving lives through technology.
    *   **Preferred Communication Style:** Professional, empathetic.
    *   **Expected Values:** Customers first, Quality and Integrity, Team up to win.
    *   **Typical Role Expectations:** Medical software, IoT, health informatics.
    *   **Keywords:** HealthTech, IoT, Medical Devices, Software, Data Science.
    """,
    "General Motors": """
    **Company Analysis: General Motors (GM)**
    *   **Tone:** Automotive, transforming, "Zero Crashes, Zero Emissions, Zero Congestion".
    *   **Hiring Culture:** Transitioning from mechanical to software-defined vehicles.
    *   **Preferred Communication Style:** Professional, safety-conscious.
    *   **Expected Values:** Customers, Relationships, Excellence.
    *   **Typical Role Expectations:** EV platforms, autonomous driving (Cruise), embedded software.
    *   **Keywords:** Automotive, EV, Autonomous Driving, Embedded, C++, Software-Defined Vehicle.
    """,
    "Ford": """
    **Company Analysis: Ford**
    *   **Tone:** Legacy, tough, "Built Ford Tough".
    *   **Hiring Culture:** Focus on mobility and electrification.
    *   **Preferred Communication Style:** Direct, practical.
    *   **Expected Values:** Put People First, Do the Right Thing, Create Tomorrow.
    *   **Typical Role Expectations:** Connected vehicles, EV software, manufacturing tech.
    *   **Keywords:** Automotive, Mobility, EV, Connected Car, Embedded Systems.
    """,
    "HCL": """
    **Company Analysis: HCL Technologies**
    *   **Tone:** "Ideapreneurship", employee-first.
    *   **Hiring Culture:** Encourages employees to come up with ideas.
    *   **Preferred Communication Style:** Professional, innovative.
    *   **Expected Values:** Trust, Transparency, Flexibility.
    *   **Typical Role Expectations:** Engineering R&D, infrastructure management, software services.
    *   **Keywords:** IT Services, Engineering R&D, Infrastructure, Ideapreneurship.
    """,
    "L&T Technology Services": """
    **Company Analysis: L&T Technology Services (LTTS)**
    *   **Tone:** Engineering-core, industrial, "Engineering the Change".
    *   **Hiring Culture:** Deep engineering domain expertise.
    *   **Preferred Communication Style:** Technical, domain-specific.
    *   **Expected Values:** Purpose, Performance, Passion.
    *   **Typical Role Expectations:** Mechanical engineering, embedded systems, plant engineering.
    *   **Keywords:** ER&D, Engineering Services, Embedded, Manufacturing, Industrial.
    """,
    "Mindtree": """
    **Company Analysis: Mindtree (LTIMindtree)**
    *   **Tone:** Collaborative, expert, "Born Digital".
    *   **Hiring Culture:** Values culture and expertise.
    *   **Preferred Communication Style:** Collaborative, professional.
    *   **Expected Values:** Collaborative Spirit, Unrelenting Dedication, Expert Thinking.
    *   **Typical Role Expectations:** Digital transformation, cloud, data analytics.
    *   **Keywords:** Digital, Cloud, Data, Consulting, IT Services.
    """,
    "Mphasis": """
    **Company Analysis: Mphasis**
    *   **Tone:** Applied Tech, "Geek", agile.
    *   **Hiring Culture:** "Front2Back" transformation.
    *   **Preferred Communication Style:** Professional, solution-oriented.
    *   **Expected Values:** Customer Centricity, Innovation.
    *   **Typical Role Expectations:** Cloud, cognitive services, banking tech.
    *   **Keywords:** Cloud, Cognitive, Banking, IT Services, Digital.
    """,
    "Persistent Systems": """
    **Company Analysis: Persistent Systems**
    *   **Tone:** Product-engineering, innovative, "See Beyond, Rise Above".
    *   **Hiring Culture:** Strong focus on software product engineering.
    *   **Preferred Communication Style:** Technical, innovative.
    *   **Expected Values:** Ingenuity, Responsibility, Persistence.
    *   **Typical Role Expectations:** Product development, cloud engineering, data.
    *   **Keywords:** Product Engineering, Cloud, Data, Digital, Salesforce.
    """,
    "Figma": """
    **Company Analysis: Figma**
    *   **Tone:** Design-led, collaborative, browser-first.
    *   **Hiring Culture:** Values "Build it with me". High bar for WebGL/C++.
    *   **Preferred Communication Style:** Visual, collaborative, thoughtful.
    *   **Expected Values:** Build Community, Run with it, Love your craft.
    *   **Typical Role Expectations:** Graphics programming, real-time collaboration, tool building.
    *   **Keywords:** Design Tools, WebGL, C++, Wasm, Collaboration, Real-time.
    """,
    "Notion": """
    **Company Analysis: Notion**
    *   **Tone:** Craftsmanship, tool-maker, aesthetic.
    *   **Hiring Culture:** Generalists, tool-builders, design-conscious engineers.
    *   **Preferred Communication Style:** Written, clear, beautiful.
    *   **Expected Values:** Be a pace setter, Be an owner, Be kind and direct.
    *   **Typical Role Expectations:** Block-based editing, local-first sync, productivity tools.
    *   **Keywords:** Productivity, Collaboration, React, SQLite, Design, Craft.
    """,
    "Canva": """
    **Company Analysis: Canva**
    *   **Tone:** Empowering, simple, "Design for everyone".
    *   **Hiring Culture:** "Crazy Big Goals". Values simplicity.
    *   **Preferred Communication Style:** Visual, simple, inclusive.
    *   **Expected Values:** Be a Force for Good, Empower Others, Pursue Excellence.
    *   **Typical Role Expectations:** Graphics rendering, frontend performance, AI design tools.
    *   **Keywords:** Design, Graphics, Web, AI, TypeScript, Java.
    """,
    "Razorpay": """
    **Company Analysis: Razorpay**
    *   **Tone:** FinTech, developer-first, "Powering Digital Payments".
    *   **Hiring Culture:** Values "Outscaling" and "Ownership".
    *   **Preferred Communication Style:** Data-driven, transparent.
    *   **Expected Values:** Customer First, Transparency, Excellence.
    *   **Typical Role Expectations:** Payment gateways, banking APIs, high availability.
    *   **Keywords:** FinTech, Payments, API, PHP, Go, India.
    """,
    "Cred": """
    **Company Analysis: Cred**
    *   **Tone:** Exclusive, design-heavy, premium.
    *   **Hiring Culture:** High bar for design and engineering quality. "Trust".
    *   **Preferred Communication Style:** Sophisticated, design-conscious.
    *   **Expected Values:** Trust, Excellence, Design.
    *   **Typical Role Expectations:** Mobile app polish, backend scalability, rewards systems.
    *   **Keywords:** FinTech, Design, Mobile, Backend, Premium, Trust.
    """
}

def get_company_prompt(company_name):
    """
    Retrieves the prompt for a specific company.
    If the company is not found, returns a generic prompt.
    Handles case-insensitive matching and partial matches (e.g., "Google India" -> "Google").
    """
    if not company_name:
        return "Company specific data not available. Analyze based on general industry standards."

    company_name_lower = company_name.lower().strip()
    
    # 1. Direct lookup (fastest)
    if company_name in COMPANY_PROMPTS:
        logger.info("Selected company prompt via direct match: %s", safe_log_text(company_name))
        return COMPANY_PROMPTS[company_name]
        
    # 2. Case-insensitive lookup
    for key, prompt in COMPANY_PROMPTS.items():
        if key.lower() == company_name_lower:
            logger.info(
                "Selected company prompt via case-insensitive match: %s",
                safe_log_text(key),
            )
            return prompt
            
    # 3. Substring lookup (e.g., "Google India" contains "google")
    # We look for the LONGEST key that matches to avoid false positives (e.g. "Go" matching "Google" if "Go" was a company)
    # But here we are checking if KEY is in INPUT.
    # e.g. Input: "Senior Software Engineer at Google" -> Key "Google" is in input.
    # e.g. Input: "Google India" -> Key "Google" is in input.
    
    matched_prompt = None
    longest_match_len = 0
    matched_key = None
    
    for key, prompt in COMPANY_PROMPTS.items():
        key_lower = key.lower()
        if key_lower in company_name_lower:
            if len(key_lower) > longest_match_len:
                longest_match_len = len(key_lower)
                matched_prompt = prompt
                matched_key = key
                
    if matched_prompt:
        logger.info(
            "Selected company prompt via substring match: %s",
            safe_log_text(matched_key),
        )
        return matched_prompt

    # 4. Reverse Substring lookup (Input in Key)
    # e.g. Input: "Tata" -> Key "Tata Consultancy Services" contains input.
    matches = []

    for key, prompt in COMPANY_PROMPTS.items():
        key_lower = key.lower()
        if company_name_lower in key_lower:
            matches.append(key)

    if matches:
        # Sort matches:
        # 1. Starts with input (priority)
        # 2. Length of key
        def sort_key(k):
            k_lower = k.lower()
            starts_with = k_lower.startswith(company_name_lower)
            return (not starts_with, len(k))

        matches.sort(key=sort_key)
        best_match_key = matches[0]
        logger.info(
            "Selected company prompt via reverse substring match: %s",
            safe_log_text(best_match_key),
        )
        return COMPANY_PROMPTS[best_match_key]

    # 5. Fuzzy lookup (Handle typos)
    close_matches = difflib.get_close_matches(company_name, COMPANY_PROMPTS.keys(), n=1, cutoff=0.6)
    
    if close_matches:
        matched_key = close_matches[0]
        logger.info(
            "Selected company prompt via fuzzy match: matched=%s input=%s",
            safe_log_text(matched_key),
            safe_log_text(company_name),
        )
        return COMPANY_PROMPTS[matched_key]

    logger.info(
        "No specific company prompt found for input=%s; using default.",
        safe_log_text(company_name),
    )
    return "Company specific data not available. Analyze based on general industry standards."
