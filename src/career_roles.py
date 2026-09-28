"""
Career Roles Database & Taxonomy Module
Contains curated industry career roles, required core/secondary skills,
step-by-step learning roadmaps, and hands-on portfolio project recommendations.
"""

from typing import Dict, List, Any

CAREER_ROLES: Dict[str, Dict[str, Any]] = {
    "Data Scientist": {
        "category": "Data Science & Machine Learning",
        "description": "Applies statistical modeling, machine learning, and exploratory data analysis to solve complex business problems.",
        "required_core_skills": ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Statistical Analysis", "Data Visualization"],
        "secondary_skills": ["Deep Learning", "TensorFlow", "PyTorch", "Natural Language Processing (NLP)", "Tableau", "Power BI", "R", "Feature Engineering", "Git"],
        "learning_roadmap": [
            {
                "order": 1,
                "skill": "Python & SQL Fundamentals",
                "focus": "Master Python for data manipulation (Pandas/NumPy) and complex SQL query drafting (aggregations, joins, window functions).",
                "milestone": "Perform end-to-end data extraction and statistical summaries on real-world datasets."
            },
            {
                "order": 2,
                "skill": "Exploratory Data Analysis & Visualization",
                "focus": "Learn Seaborn, Matplotlib, and statistical hypothesis testing (A/B testing, distributions, p-values).",
                "milestone": "Create insightful exploratory data reports discovering patterns and correlations."
            },
            {
                "order": 3,
                "skill": "Classical Machine Learning (Scikit-Learn)",
                "focus": "Supervised & unsupervised algorithms (Regression, Random Forest, XGBoost, K-Means), cross-validation, and metrics (ROC-AUC, F1-Score).",
                "milestone": "Build predictive models with automated feature engineering pipelines."
            },
            {
                "order": 4,
                "skill": "Deep Learning & NLP / Computer Vision",
                "focus": "Neural network architectures (PyTorch/TensorFlow), transfer learning, Hugging Face Transformers, and text/image processing.",
                "milestone": "Train fine-tuned models for sentiment analysis or computer vision classification."
            },
            {
                "order": 5,
                "skill": "Model Deployment & MLOps Basics",
                "focus": "FastAPI, Docker containerization, Streamlit interactive dashboards, MLflow experiment tracking, and cloud endpoints.",
                "milestone": "Deploy a live public web application serving model predictions in real time."
            }
        ],
        "project_recommendations": [
            {
                "title": "Customer Churn Prediction with Explainable AI (SHAP)",
                "difficulty": "Intermediate",
                "tech_stack": ["Python", "Pandas", "Scikit-Learn", "XGBoost", "SHAP", "Streamlit"],
                "description": "Predict customer churn probability for a SaaS/telecom platform and generate interactive SHAP force plots explaining feature importance to stakeholders.",
                "impact": "Demonstrates end-to-end ML workflow, model interpretability, and business KPI optimization."
            },
            {
                "title": "E-Commerce Recommendation Engine (Collaborative & Content-Based)",
                "difficulty": "Intermediate",
                "tech_stack": ["Python", "PySpark / Scikit-Learn", "FastAPI", "PostgreSQL"],
                "description": "Build a hybrid recommendation system leveraging matrix factorization (SVD) and cosine similarity to deliver tailored product suggestions.",
                "impact": "Highlights algorithms used in production at Netflix/Amazon and backend API integration."
            },
            {
                "title": "Multi-Modal Sentiment & Topic Modeling Dashboard",
                "difficulty": "Advanced",
                "tech_stack": ["Python", "Hugging Face Transformers", "BERTopic", "PyTorch", "Docker"],
                "description": "Ingest live customer review streams, extract sentiment, and cluster evolving discussion topics using state-of-the-art transformer models.",
                "impact": "Showcases modern NLP, unsupervised embeddings, and scalable deployment."
            }
        ]
    },
    "Machine Learning Engineer": {
        "category": "Data Science & Machine Learning",
        "description": "Designs, trains, tests, and deploys high-throughput machine learning pipelines and models into scalable production systems.",
        "required_core_skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Scikit-Learn", "Docker", "Git", "FastAPI"],
        "secondary_skills": ["MLOps", "Kubernetes", "AWS", "CI/CD", "MLflow", "Pandas", "SQL", "Generative AI", "LLMs"],
        "learning_roadmap": [
            {
                "order": 1,
                "skill": "Deep Learning Frameworks (PyTorch / TensorFlow)",
                "focus": "Master custom neural network layers, loss functions, GPU acceleration with CUDA, and backpropagation mechanics.",
                "milestone": "Build and train CNNs and Transformer models from scratch and via transfer learning."
            },
            {
                "order": 2,
                "skill": "API Development & Model Serving",
                "focus": "Wrap inference pipelines in asynchronous FastAPI / TorchServe endpoints with batching and caching.",
                "milestone": "Expose low-latency prediction endpoints with Swagger API docs."
            },
            {
                "order": 3,
                "skill": "Containerization & Dockerization",
                "focus": "Write lightweight multi-stage Dockerfiles for Python ML environments, optimizing image size and runtime dependencies.",
                "milestone": "Run reproducible containerized inference services locally and in the cloud."
            },
            {
                "order": 4,
                "skill": "MLOps, Experiment Tracking & CI/CD",
                "focus": "Integrate MLflow or Weights & Biases for experiment tracking, DVC for dataset versioning, and GitHub Actions for testing.",
                "milestone": "Automate model retraining and evaluation on new data ingestion."
            },
            {
                "order": 5,
                "skill": "Cloud Deployment & Scalable Orchestration (AWS / Kubernetes)",
                "focus": "Deploy models to AWS SageMaker or Kubernetes clusters (KServe/BentoML) with horizontal autoscaling.",
                "milestone": "Maintain high-availability production endpoints with logging and data drift alerts."
            }
        ],
        "project_recommendations": [
            {
                "title": "Real-Time Object Detection & Tracking Inference Microservice",
                "difficulty": "Intermediate",
                "tech_stack": ["Python", "YOLOv8", "OpenCV", "FastAPI", "Docker"],
                "description": "Develop a containerized API that processes live video streams, detects objects, and streams annotated frames with sub-50ms latency.",
                "impact": "Proves deep computer vision engineering, asynchronous processing, and containerization skills."
            },
            {
                "title": "Automated End-to-End MLOps Pipeline with MLflow & GitHub Actions",
                "difficulty": "Advanced",
                "tech_stack": ["Python", "MLflow", "DVC", "Docker", "GitHub Actions", "AWS S3"],
                "description": "Construct a continuous training pipeline that pulls updated data, validates metrics against a production baseline, and auto-deploys passing models.",
                "impact": "Gold standard for modern ML Engineering roles."
            },
            {
                "title": "Production RAG Assistant with Vector Search & LangChain",
                "difficulty": "Advanced",
                "tech_stack": ["Python", "LangChain", "Qdrant / ChromaDB", "FastAPI", "Docker", "LLMs"],
                "description": "Build an enterprise document question-answering system using hybrid dense/sparse vector retrieval and prompt evaluation guards.",
                "impact": "Demonstrates cutting-edge Generative AI engineering and retrieval optimization."
            }
        ]
    },
    "Data Analyst": {
        "category": "Business Intelligence & Analytics",
        "description": "Transforms raw structured and unstructured data into meaningful actionable business intelligence and dashboards.",
        "required_core_skills": ["SQL", "Excel", "Power BI", "Tableau", "Python", "Data Visualization", "Statistical Analysis"],
        "secondary_skills": ["Pandas", "DAX", "Power Query", "A/B Testing", "KPI Tracking", "Google Analytics", "Git"],
        "learning_roadmap": [
            {
                "order": 1,
                "skill": "Advanced SQL & Database Querying",
                "focus": "Master complex joins, subqueries, CTEs, window functions (RANK, ROW_NUMBER), and data cleaning inside relational databases.",
                "milestone": "Solve intermediate-to-advanced business SQL problems on real transaction databases."
            },
            {
                "order": 2,
                "skill": "BI Tools (Power BI / Tableau)",
                "focus": "Build interactive drill-down reports, data modeling with star schemas, DAX measures, and dashboard storytelling.",
                "milestone": "Publish executive-ready KPI dashboards with real-time filters."
            },
            {
                "order": 3,
                "skill": "Python for Data Analysis (Pandas & Seaborn)",
                "focus": "Automate data cleaning scripts, handle missing data, parse timestamps, and visualize distributions in Jupyter notebooks.",
                "milestone": "Replace manual Excel spreadsheets with reproducible Python scripts."
            },
            {
                "order": 4,
                "skill": "Business Acumen & Statistical Testing",
                "focus": "A/B test design, conversion funnel analysis, customer lifetime value (CLV) calculation, and cohort retention matrices.",
                "milestone": "Deliver a data-backed business recommendation presentation with executive summary."
            }
        ],
        "project_recommendations": [
            {
                "title": "Executive Sales & Revenue KPI Dashboard (Power BI / Tableau)",
                "difficulty": "Beginner",
                "tech_stack": ["Power BI / Tableau", "SQL", "Excel", "DAX"],
                "description": "Design an executive dashboard tracking MRR, customer acquisition cost (CAC), regional performance, and year-over-year revenue growth.",
                "impact": "Directly exhibits commercial business intelligence and data visualization capability."
            },
            {
                "title": "E-Commerce Cohort Retention & Funnel Analysis",
                "difficulty": "Intermediate",
                "tech_stack": ["Python", "Pandas", "SQL", "Plotly", "Streamlit"],
                "description": "Analyze multi-year user purchase journeys, compute monthly cohort retention rates, and pinpoint checkout drop-off stages.",
                "impact": "Demonstrates strong product analytics and data-driven growth insights."
            }
        ]
    },
    "Software Developer": {
        "category": "General Software Engineering",
        "description": "Builds robust, maintainable, and scalable software applications across platforms and stacks.",
        "required_core_skills": ["Python", "Java", "C++", "JavaScript", "Data Structures", "Algorithms", "Git", "SQL", "Object-Oriented Programming (OOP)"],
        "secondary_skills": ["REST API", "Docker", "Linux", "Unit Testing", "CI/CD", "Design Patterns", "Agile"],
        "learning_roadmap": [
            {
                "order": 1,
                "skill": "Core Programming & OOP Principles",
                "focus": "Solidify mastery in a core language (Java, Python, C++, or TypeScript), OOP concepts, and clean code practices.",
                "milestone": "Implement robust classes adhering to SOLID principles and modular design."
            },
            {
                "order": 2,
                "skill": "Data Structures & Algorithmic Complexity",
                "focus": "Master Trees, Graphs, Hash Maps, Dynamic Programming, and Big-O space/time optimization.",
                "milestone": "Confidently solve medium-level algorithmic coding challenges."
            },
            {
                "order": 3,
                "skill": "Database Design & API Integration",
                "focus": "Relational schema design, normalization, indexing, and developing/consuming RESTful APIs.",
                "milestone": "Build a CRUD service connected to a persistent SQL database."
            },
            {
                "order": 4,
                "skill": "Testing, Version Control & CI/CD",
                "focus": "Unit testing frameworks (Pytest, JUnit, Jest), Git branching strategies, and automated GitHub Actions workflows.",
                "milestone": "Achieve 85%+ test coverage on a multi-module repository with automated builds."
            }
        ],
        "project_recommendations": [
            {
                "title": "Distributed Task Scheduler & Job Queue",
                "difficulty": "Intermediate",
                "tech_stack": ["Python / Java", "Redis", "PostgreSQL", "Docker"],
                "description": "Create a background worker system that handles delayed job dispatching, retry logic with exponential backoff, and worker concurrency.",
                "impact": "Showcases systems design, asynchronous concurrency, and data persistence."
            },
            {
                "title": "Collaborative Real-Time Code & Note Editor",
                "difficulty": "Advanced",
                "tech_stack": ["TypeScript", "Node.js / Python", "WebSockets", "Docker"],
                "description": "Build a real-time multiplayer document editor with operational transformation or CRDTs for conflict-free synchronization.",
                "impact": "Highlights complex networking, state synchronization, and scalable architecture."
            }
        ]
    },
    "Full Stack Developer": {
        "category": "Full Stack & Web Development",
        "description": "Architects and develops both client-facing frontend user interfaces and robust backend services and databases.",
        "required_core_skills": ["JavaScript", "TypeScript", "React", "Node.js", "HTML", "CSS", "REST API", "SQL", "MongoDB", "Git"],
        "secondary_skills": ["Next.js", "Express", "PostgreSQL", "Tailwind CSS", "Docker", "GraphQL", "CI/CD", "AWS"],
        "learning_roadmap": [
            {
                "order": 1,
                "skill": "Modern Frontend (React + TypeScript + Tailwind)",
                "focus": "Hooks, state management (Zustand/Redux), responsive layout, accessibility, and type safety.",
                "milestone": "Build interactive, pixel-perfect user interfaces with dynamic component states."
            },
            {
                "order": 2,
                "skill": "Backend & RESTful APIs (Node.js / Express / Next.js)",
                "focus": "Server routing, middleware, JWT authentication, rate limiting, and error handling.",
                "milestone": "Construct secure, production-ready backend API endpoints."
            },
            {
                "order": 3,
                "skill": "Databases & ORMs (PostgreSQL / Prisma / MongoDB)",
                "focus": "Relational data modeling, migrations, indexing, and NoSQL document storage.",
                "milestone": "Architect multi-table schemas with ACID compliance and query optimization."
            },
            {
                "order": 4,
                "skill": "Full Stack Architecture & Cloud Deployment",
                "focus": "Full-stack integration, Docker containerization, CI/CD pipelines, and cloud hosting (Vercel, AWS EC2/ECS).",
                "milestone": "Deploy a complete SaaS application with payment gateway and email notifications."
            }
        ],
        "project_recommendations": [
            {
                "title": "Full-Stack SaaS Management Platform with Stripe & RBAC",
                "difficulty": "Intermediate",
                "tech_stack": ["React", "Next.js", "TypeScript", "Node.js", "PostgreSQL", "Tailwind CSS", "Stripe API"],
                "description": "Build a complete subscription billing SaaS with role-based access control, team workspaces, dark/light theme, and analytics.",
                "impact": "Proves readiness for commercial product engineering teams."
            },
            {
                "title": "Real-Time Marketplace & Chat Application",
                "difficulty": "Advanced",
                "tech_stack": ["React", "Express", "Node.js", "MongoDB", "WebSockets / Socket.io", "AWS S3", "Docker"],
                "description": "Create an online marketplace featuring user listings, image uploads to cloud storage, instant peer-to-peer messaging, and live search.",
                "impact": "Covers high-concurrency communications, file storage, and complex state."
            }
        ]
    },
    "Backend Engineer": {
        "category": "Backend & Systems Engineering",
        "description": "Specializes in core backend services, distributed systems, caching, microservices, and database performance.",
        "required_core_skills": ["Python", "Java", "Go", "Node.js", "SQL", "PostgreSQL", "Redis", "REST API", "Microservices", "Docker"],
        "secondary_skills": ["Kafka", "gRPC", "Kubernetes", "AWS", "FastAPI", "Spring Boot", "CI/CD", "Linux", "System Design"],
        "learning_roadmap": [
            {
                "order": 1,
                "skill": "Server Frameworks & Protocol Mastery",
                "focus": "Deep dive into FastAPI / Spring Boot / Go Gin, HTTP/2, gRPC, and REST conventions.",
                "milestone": "Build lightning-fast modular microservices."
            },
            {
                "order": 2,
                "skill": "High-Performance Databases & Caching (PostgreSQL & Redis)",
                "focus": "Transaction isolation levels, query plan EXPLAIN ANALYZE, indexing strategies, Redis caching and pub/sub.",
                "milestone": "Optimize database throughput and reduce latency under simulated loads."
            },
            {
                "order": 3,
                "skill": "Message Brokers & Asynchronous Event Streaming (Kafka / RabbitMQ)",
                "focus": "Event-driven architecture, consumer groups, partition management, and idempotency.",
                "milestone": "Implement fault-tolerant event processing pipelines."
            },
            {
                "order": 4,
                "skill": "System Design, Scalability & Security",
                "focus": "Load balancing, rate limiting, circuit breakers, OAuth2/JWT security, and horizontal scaling.",
                "milestone": "Design and simulate a high-availability distributed architecture."
            }
        ],
        "project_recommendations": [
            {
                "title": "High-Throughput URL Shortener & Analytics Engine",
                "difficulty": "Intermediate",
                "tech_stack": ["Go / Python FastAPI", "PostgreSQL", "Redis", "Docker", "Prometheus"],
                "description": "Architect a service capable of redirecting 10k+ requests/sec with Redis caching, Base62 encoding, and geo-analytics logging.",
                "impact": "Classic system design showcase highlighting sub-millisecond latency."
            },
            {
                "title": "Event-Driven Order Processing System with Kafka & Microservices",
                "difficulty": "Advanced",
                "tech_stack": ["Java Spring Boot / Python", "Apache Kafka", "PostgreSQL", "Docker", "Kubernetes"],
                "description": "Create independent microservices (Order, Payment, Inventory, Notification) coordinating via Kafka events with Saga pattern transaction rollback.",
                "impact": "Direct demonstration of enterprise-level distributed backend engineering."
            }
        ]
    },
    "DevOps Engineer": {
        "category": "DevOps & Cloud Engineering",
        "description": "Automates software delivery, provisions cloud infrastructure, and ensures system reliability, security, and scalability.",
        "required_core_skills": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Linux", "Git", "GitHub Actions", "Bash"],
        "secondary_skills": ["Python", "Ansible", "Prometheus", "Grafana", "Azure", "GCP", "Helm", "Nginx", "Site Reliability Engineering (SRE)"],
        "learning_roadmap": [
            {
                "order": 1,
                "skill": "Linux Systems & Shell Scripting",
                "focus": "File systems, process management, networking (DNS, IPTables, SSH), and automated Bash/Python scripts.",
                "milestone": "Automate server maintenance and security hardening tasks."
            },
            {
                "order": 2,
                "skill": "Docker Containerization & Multi-Stage Builds",
                "focus": "Build secure, minimal OCI container images, Docker compose multi-service environments, and networking.",
                "milestone": "Containerize legacy and modern multi-tier web applications."
            },
            {
                "order": 3,
                "skill": "CI/CD Automation Pipelines (GitHub Actions / GitLab CI)",
                "focus": "Automated linting, testing, security vulnerability scanning (Trivy/SonarQube), and automated cloud deployment.",
                "milestone": "Build zero-downtime deployment pipelines triggered on main branch merges."
            },
            {
                "order": 4,
                "skill": "Infrastructure as Code (Terraform) & Cloud (AWS)",
                "focus": "Provision VPCs, subnets, EC2, ECS/EKS, S3, RDS, and IAM roles declaratively with state management.",
                "milestone": "Spin up complete production cloud environments with a single 'terraform apply'."
            },
            {
                "order": 5,
                "skill": "Kubernetes Orchestration & Observability (Prometheus / Grafana)",
                "focus": "Deployments, Services, Ingress, Helm charts, Horizontal Pod Autoscaling (HPA), metrics scraping, and alert routing.",
                "milestone": "Manage production Kubernetes cluster with auto-healing and real-time observability dashboards."
            }
        ],
        "project_recommendations": [
            {
                "title": "GitOps Kubernetes Deployment Pipeline with ArgoCD & Helm",
                "difficulty": "Intermediate",
                "tech_stack": ["Kubernetes", "Helm", "ArgoCD", "Docker", "GitHub Actions"],
                "description": "Implement a GitOps workflow where changes pushed to Git repositories automatically sync to a live Kubernetes cluster.",
                "impact": "Exhibits industry-standard modern cloud infrastructure practices."
            },
            {
                "title": "Multi-Tier Cloud Infrastructure on AWS using Terraform & Monitoring",
                "difficulty": "Advanced",
                "tech_stack": ["Terraform", "AWS (VPC, EKS, RDS)", "Prometheus", "Grafana", "Trivy"],
                "description": "Write reusable Terraform modules provisioning a secure AWS VPC, auto-scaling EKS cluster, managed RDS database, and Grafana monitoring.",
                "impact": "Demonstrates production readiness for Senior DevOps/SRE positions."
            }
        ]
    },
    "Data Engineer": {
        "category": "Data Engineering & Big Data",
        "description": "Builds scalable data architectures, automated ETL/ELT pipelines, and data warehouse infrastructures for analytics and ML.",
        "required_core_skills": ["Python", "SQL", "Apache Spark", "PySpark", "Apache Kafka", "Airflow", "Data Warehousing", "PostgreSQL", "Docker"],
        "secondary_skills": ["Snowflake", "BigQuery", "dbt", "AWS Redshift", "Delta Lake", "Hadoop", "Pandas", "Git", "CI/CD"],
        "learning_roadmap": [
            {
                "order": 1,
                "skill": "Advanced SQL & Dimensional Data Modeling",
                "focus": "Star schemas, Snowflake schemas, slowly changing dimensions (SCD Type 1 & 2), and analytical window queries.",
                "milestone": "Design scalable data warehouse schemas optimized for reporting."
            },
            {
                "order": 2,
                "skill": "Distributed Data Processing with Apache Spark & PySpark",
                "focus": "RDDs, DataFrames, transformations, actions, broadcast joins, partitioning, and memory tuning.",
                "milestone": "Process multi-gigabyte datasets across distributed nodes efficiently."
            },
            {
                "order": 3,
                "skill": "Pipeline Orchestration with Apache Airflow",
                "focus": "DAG design, operators, sensors, XComs, connection pools, and error alerting.",
                "milestone": "Construct scheduled, self-healing data pipeline workflows."
            },
            {
                "order": 4,
                "skill": "Modern Data Stack & Cloud Warehouses (Snowflake / BigQuery / dbt)",
                "focus": "dbt transformations, automated data testing, data lineage, and cloud warehouse optimization.",
                "milestone": "Build automated ELT pipelines transforming raw staging data into clean analytics tables."
            }
        ],
        "project_recommendations": [
            {
                "title": "Real-Time Streaming ETL Pipeline with Kafka, Spark & Delta Lake",
                "difficulty": "Advanced",
                "tech_stack": ["Python", "Apache Kafka", "Apache Spark (Structured Streaming)", "Delta Lake", "Docker", "PostgreSQL"],
                "description": "Ingest live high-frequency financial or IoT events via Kafka, process sliding window aggregations in Spark, and write ACID transactions to Delta Lake.",
                "impact": "Demonstrates real-time distributed data engineering capabilities."
            },
            {
                "title": "Automated Cloud Data Warehouse with Airflow, dbt & Snowflake",
                "difficulty": "Intermediate",
                "tech_stack": ["Apache Airflow", "dbt", "Snowflake / BigQuery", "Python", "SQL"],
                "description": "Orchestrate daily batch ingestion from external APIs, apply dbt SQL modeling with automated data quality test suites, and generate schema documentation.",
                "impact": "Direct match for modern analytics engineering and data warehouse roles."
            }
        ]
    },
    "Cybersecurity Analyst": {
        "category": "Cybersecurity & InfoSec",
        "description": "Protects networks, computer systems, and sensitive data from cyber threats, vulnerabilities, and unauthorized access.",
        "required_core_skills": ["Cybersecurity", "Network Security", "Penetration Testing", "Vulnerability Assessment", "SIEM", "Linux", "Python", "TCP/IP"],
        "secondary_skills": ["Wireshark", "Metasploit", "Burp Suite", "OWASP", "Firewall", "SOC", "Incident Response", "Cryptography", "Identity and Access Management"],
        "learning_roadmap": [
            {
                "order": 1,
                "skill": "Networking Protocols & Linux Hardening",
                "focus": "TCP/IP model, packet analysis with Wireshark, DNS, SSL/TLS, Linux access permissions, and firewall rules (UFW/IPTables).",
                "milestone": "Identify and dissect anomalous network traffic and secure server ports."
            },
            {
                "order": 2,
                "skill": "Web Application Security & OWASP Top 10",
                "focus": "SQL injection, XSS, CSRF, broken authentication, IDOR, and security auditing with Burp Suite.",
                "milestone": "Conduct structured vulnerability scans and manual security audits of web apps."
            },
            {
                "order": 3,
                "skill": "Security Information & Event Management (SIEM / SOC)",
                "focus": "Log analysis in Splunk/Elasticsearch, writing detection rules, threat hunting, and incident triage.",
                "milestone": "Build a simulated SOC alert pipeline detecting brute-force and privilege escalation attacks."
            },
            {
                "order": 4,
                "skill": "Ethical Hacking & Vulnerability Remediation",
                "focus": "Reconnaissance, Nmap, Metasploit, exploit remediation, and writing professional security audit reports.",
                "milestone": "Complete structured CTF challenges and draft executive risk assessment reports."
            }
        ],
        "project_recommendations": [
            {
                "title": "Automated Network Vulnerability Scanner & Port Auditor",
                "difficulty": "Intermediate",
                "tech_stack": ["Python", "Nmap Library", "Scapy", "Linux", "Streamlit / CLI"],
                "description": "Develop a multi-threaded Python scanner that discovers active subnet hosts, audits open ports, banners service versions, and flags known CVEs.",
                "impact": "Exhibits scripting, networking knowledge, and vulnerability assessment skills."
            },
            {
                "title": "Simulated SIEM Dashboard & Intrusion Detection System",
                "difficulty": "Intermediate",
                "tech_stack": ["Python", "Elasticsearch / OpenSearch", "Kibana", "Suricata / Snort", "Docker"],
                "description": "Deploy Suricata IDS in containers, ingest network alerts into Elasticsearch, and visualize threat patterns on interactive Kibana dashboards.",
                "impact": "Direct alignment with SOC Analyst and Security Engineer roles."
            }
        ]
    }
}


def get_all_career_roles() -> List[str]:
    """Returns list of available career role names."""
    return list(CAREER_ROLES.keys())


def get_role_details(role_name: str) -> Dict[str, Any]:
    """Retrieves full specifications for a given career role."""
    if role_name in CAREER_ROLES:
        return CAREER_ROLES[role_name]
    
    # Fallback default role structure
    return {
        "category": "General Software Engineering",
        "description": "General technology role focusing on software development and technical problem solving.",
        "required_core_skills": ["Python", "SQL", "Git", "Data Structures", "Algorithms"],
        "secondary_skills": ["Docker", "Linux", "REST API", "Unit Testing"],
        "learning_roadmap": [
            {"order": 1, "skill": "Core Programming", "focus": "Master algorithmic problem solving and data structures.", "milestone": "Write clean, tested code."},
            {"order": 2, "skill": "Database & API Design", "focus": "Understand relational schemas and REST APIs.", "milestone": "Build a CRUD service."}
        ],
        "project_recommendations": [
            {"title": "Full-Stack Web Application", "difficulty": "Intermediate", "tech_stack": ["Python", "SQL", "Git"], "description": "Create a complete CRUD application with database persistence.", "impact": "Proves end-to-end technical competency."}
        ]
    }
