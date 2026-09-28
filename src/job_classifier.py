"""
ML Job Category Classifier Module
Trains and serves a Multi-Class Supervised NLP Classifier to predict the candidate's optimal career domain.
Uses TF-IDF Feature Extraction + Multinomial Naive Bayes / Calibrated Classifier for probability distributions.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
from src.text_cleaner import clean_for_nlp

# Default categories
JOB_CATEGORIES = [
    "Data Science & Machine Learning",
    "Full Stack & Web Development",
    "DevOps & Cloud Engineering",
    "Cybersecurity & InfoSec",
    "Data Engineering & Big Data",
    "Mobile App Development",
    "UI/UX Design",
    "Quality Assurance & Testing",
    "Backend & Systems Engineering",
    "Business Intelligence & Analytics"
]

class JobCategoryClassifier:
    def __init__(self, model_path: str = None):
        if not model_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "job_classifier_model.pkl")
        self.model_path = model_path
        self.pipeline = None
        self.load_or_train_model()

    def load_or_train_model(self):
        """Loads model from disk if available, otherwise trains on synthetic dataset."""
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                return
            except Exception:
                pass
        self.train_and_save_model()

    def train_and_save_model(self, data_path: str = None) -> float:
        """Trains the ML pipeline and saves to disk."""
        df = self._get_or_create_training_data(data_path)
        
        # Preprocess text
        df['clean_text'] = df['text'].apply(lambda x: clean_for_nlp(str(x)))
        
        # Build NLP Pipeline: TF-IDF with (1, 2) ngrams + Logistic Regression with Balanced weights
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=4000,
                sublinear_tf=True,
                min_df=1
            )),
            ('clf', LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                C=2.0,
                solver='lbfgs'
            ))
        ])

        self.pipeline.fit(df['clean_text'], df['category'])

        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)

        train_acc = accuracy_score(df['category'], self.pipeline.predict(df['clean_text']))
        return round(train_acc * 100, 2)

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predicts top job categories with confidence probabilities.
        """
        if not self.pipeline:
            self.load_or_train_model()

        clean = clean_for_nlp(text)
        if not clean or len(clean.split()) < 3:
            return {
                'predicted_category': 'General Software Engineering',
                'confidence': 0.0,
                'category_probabilities': {c: 0.0 for c in JOB_CATEGORIES},
                'top_3_categories': [('General Software Engineering', 0.0)]
            }

        # Predict probabilities
        probs = self.pipeline.predict_proba([clean])[0]
        classes = self.pipeline.classes_

        class_prob_dict = {cls: round(float(prob) * 100, 2) for cls, prob in zip(classes, probs)}
        
        # Sort by confidence descending
        sorted_probs = sorted(class_prob_dict.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_conf = sorted_probs[0]

        return {
            'predicted_category': top_cat,
            'confidence': top_conf,
            'category_probabilities': class_prob_dict,
            'top_3_categories': sorted_probs[:3]
        }

    def _get_or_create_training_data(self, data_path: str = None) -> pd.DataFrame:
        """Loads training CSV or generates a rich training set."""
        if data_path and os.path.exists(data_path):
            return pd.read_csv(data_path)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_csv = os.path.join(base_dir, "data", "training_data.csv")
        if os.path.exists(default_csv):
            return pd.read_csv(default_csv)

        # Generate rich training dataset
        df = self._generate_training_dataset()
        os.makedirs(os.path.dirname(default_csv), exist_ok=True)
        df.to_csv(default_csv, index=False)
        return df

    def _generate_training_dataset(self) -> pd.DataFrame:
        """Generates representative resume snippets across domains."""
        data = [
            # Data Science & ML
            ("Experienced Data Scientist skilled in Python, Scikit-learn, PyTorch, TensorFlow, Pandas, NumPy, Deep Learning, NLP transformers BERT GPT, statistical modeling, data visualization, predictive analytics, Jupyter notebooks.", "Data Science & Machine Learning"),
            ("Machine Learning Engineer with 4 years building computer vision and NLP models. Experience in PyTorch, OpenCV, MLflow, model deployment, hyperparameter optimization, feature engineering, classification and regression algorithms.", "Data Science & Machine Learning"),
            ("AI Researcher working on Large Language Models LLMs, RAG retrieval augmented generation, LangChain, prompt engineering, vector databases, fine-tuning Llama, Hugging Face transformers, reinforcement learning from human feedback.", "Data Science & Machine Learning"),
            ("Data Analyst / Junior Data Scientist proficient in Python, SQL, Tableau, Pandas, Scipy, statistical hypothesis testing, A/B testing, exploratory data analysis, machine learning algorithms, Scikit-learn, clustering.", "Data Science & Machine Learning"),
            ("Senior ML Engineer designing real-time recommendation engines, anomaly detection, Deep Learning with Keras and PyTorch, deploying models with FastAPI and Docker on AWS SageMaker.", "Data Science & Machine Learning"),

            # Full Stack & Web Dev
            ("Full Stack Web Developer proficient in React, JavaScript, TypeScript, Next.js, Node.js, Express, HTML5, CSS3, Tailwind CSS, Redux, REST APIs, MongoDB, PostgreSQL, responsive UI development.", "Full Stack & Web Development"),
            ("Frontend Developer specialized in React.js, Vue.js, Angular, TypeScript, State management, Webpack, Vite, modern CSS, Bootstrap, Material UI, WebSockets, client-side performance optimization.", "Full Stack & Web Development"),
            ("Web Developer building interactive responsive web applications using JavaScript, React, Next.js, GraphQL, RESTful endpoints, Tailwind, Jest testing, Figma to code conversion.", "Full Stack & Web Development"),
            ("Full Stack Software Engineer with expertise in MERN stack (MongoDB, Express, React, Node.js), Redux Toolkit, Next.js, HTML, CSS, Git, modern web standards, authentication with JWT.", "Full Stack & Web Development"),
            ("Senior Frontend Architect building single page applications SPA with React, TypeScript, micro-frontends, responsive web design, progressive web apps PWA, automated UI testing with Cypress.", "Full Stack & Web Development"),

            # DevOps & Cloud
            ("DevOps Engineer with strong experience in AWS, EC2, S3, Docker containerization, Kubernetes orchestration, Terraform infrastructure as code, CI/CD pipelines with Jenkins and GitHub Actions, Linux administration.", "DevOps & Cloud Engineering"),
            ("Cloud Architect / Site Reliability Engineer SRE managing multi-cloud infrastructure on Azure and GCP, Helm charts, Prometheus, Grafana monitoring, Ansible automation, bash scripting, zero-downtime deployments.", "DevOps & Cloud Engineering"),
            ("DevOps Specialist focused on automated continuous integration and continuous deployment CI/CD, Docker, Kubernetes clusters, Terraform, Linux server hardening, GitLab CI, AWS IAM, cloud security.", "DevOps & Cloud Engineering"),
            ("Systems and Cloud Engineer experienced with Amazon Web Services, Nginx reverse proxy, microservices orchestration, CloudWatch alerts, SRE practices, high availability, serverless AWS Lambda.", "DevOps & Cloud Engineering"),
            ("Cloud Infrastructure Engineer maintaining Linux servers, containerizing legacy apps with Docker, managing Kubernetes pods, Terraform state, automated deployment scripts in Python and Bash.", "DevOps & Cloud Engineering"),

            # Cybersecurity & InfoSec
            ("Cybersecurity Analyst with background in vulnerability assessment, penetration testing, SIEM tools, SOC operations, network security, firewall configuration, OWASP top 10, incident response, ethical hacking.", "Cybersecurity & InfoSec"),
            ("Information Security Engineer skilled in Wireshark, Metasploit, Burp Suite, cryptography, SSL/TLS, IDS/IPS, zero trust architecture, SOC2 compliance, ISO 27001 auditing, CISSP principles.", "Cybersecurity & InfoSec"),
            ("Ethical Hacker / Pen Tester conducting web application security assessments, vulnerability scanning with Nessus, reverse engineering, exploit development, defense in depth, malware analysis.", "Cybersecurity & InfoSec"),
            ("SOC Analyst monitoring security logs, SIEM dashboards (Splunk/QRadar), threat hunting, incident handling, identity and access management IAM, network forensics, packet analysis.", "Cybersecurity & InfoSec"),
            ("Security Engineer implementing end-to-end encryption, OAuth2, PKI, firewall policies, endpoint security, cloud security posture management CSPM, penetration testing reports.", "Cybersecurity & InfoSec"),

            # Data Engineering & Big Data
            ("Data Engineer proficient in SQL, Python, PySpark, Apache Spark, Apache Kafka, Airflow DAG orchestration, ETL pipeline development, Snowflake, BigQuery, AWS Redshift, data warehousing.", "Data Engineering & Big Data"),
            ("Big Data Engineer building distributed streaming pipelines with Kafka, Flink, Hadoop, Hive, Spark, Delta Lake, PostgreSQL, dbt data modeling, automated data ingestion.", "Data Engineering & Big Data"),
            ("Senior Data Pipeline Architect with 5 years building scalable ETL/ELT pipelines in Python and SQL, orchestrating Airflow workflows, Databricks, data lakehouse architectures, partitioning.", "Data Engineering & Big Data"),
            ("Data Warehouse Engineer optimizing complex SQL queries, building dimensional data models, managing Snowflake schemas, ingestion pipelines with Airbyte and dbt, data quality monitoring.", "Data Engineering & Big Data"),
            ("Data Platform Engineer working with distributed systems, Spark streaming, Kafka topic partitions, NoSQL Cassandra, MongoDB, database indexing, Parquet file optimization.", "Data Engineering & Big Data"),

            # Mobile App Dev
            ("Mobile App Developer skilled in Flutter, Dart, React Native, cross-platform app development, state management Provider Bloc, Android Studio, Xcode, Google Play Console deployment.", "Mobile App Development"),
            ("Android Developer with 3 years building native apps with Kotlin, Java, Jetpack Compose, Retrofit, Room DB, MVVM architecture, Android SDK, push notifications, background services.", "Mobile App Development"),
            ("iOS Developer experienced in Swift, SwiftUI, UIKit, CoreData, Combine, CocoaPods, TestFlight, App Store guidelines, REST APIs integration, responsive mobile UI.", "Mobile App Development"),
            ("Cross-Platform Mobile Engineer developing apps in React Native and Flutter, JavaScript, TypeScript, native bridging, mobile offline sync, Firebase backend integration.", "Mobile App Development"),
            ("Senior Mobile Engineer architecting iOS and Android apps, Kotlin Multiplatform, SwiftUI, deep linking, in-app purchases, mobile CI/CD pipelines with Fastlane.", "Mobile App Development"),

            # UI/UX Design
            ("UI/UX Designer creating user-centered designs, wireframes, prototypes in Figma, Adobe XD, user research, usability testing, design systems, interaction design, information architecture.", "UI/UX Design"),
            ("Product Designer skilled in Figma, Sketch, high-fidelity mockups, customer journey mapping, persona development, UX writing, mobile and web responsive UI, design tokens.", "UI/UX Design"),
            ("UX Researcher & UI Designer conducting user interviews, A/B testing prototypes, heuristic evaluations, micro-interactions, accessibility WCAG compliance, Canva, Photoshop.", "UI/UX Design"),
            ("Lead UI Designer crafting brand guidelines, component libraries in Figma, interactive design prototypes, usability audits, developer handoff specs.", "UI/UX Design"),
            ("Digital Product Designer combining UX research, wireframing, rapid prototyping in Figma, visual design, design thinking workshops, user feedback synthesis.", "UI/UX Design"),

            # QA & Testing
            ("QA Automation Engineer with extensive experience in Selenium WebDriver, Python pytest, Java TestNG, Cypress, Playwright, API testing with Postman, test automation frameworks.", "Quality Assurance & Testing"),
            ("Software Development Engineer in Test SDET creating CI/CD automated test suites, end-to-end testing, JUnit, performance testing with JMeter, regression testing, bug tracking in Jira.", "Quality Assurance & Testing"),
            ("Quality Assurance Specialist executing manual and automated test cases, test planning, boundary value analysis, functional testing, exploratory testing, Postman collections.", "Quality Assurance & Testing"),
            ("Test Automation Architect building scalable test frameworks with Pytest and Selenium, cross-browser testing, load testing with Locust, defect management lifecycle.", "Quality Assurance & Testing"),
            ("QA Engineer specialized in web and mobile automation testing, API validation, BDD Cucumber frameworks, test reporting, continuous testing in GitHub Actions.", "Quality Assurance & Testing"),

            # Backend & Systems
            ("Backend Software Engineer specializing in Python Django FastAPI, Go Golang, microservices architecture, RESTful APIs, PostgreSQL, Redis caching, gRPC, Docker, system design.", "Backend & Systems Engineering"),
            ("Java Backend Developer building enterprise applications with Spring Boot, Hibernate, Java 17, Maven, REST APIs, MySQL, Kafka message queues, design patterns.", "Backend & Systems Engineering"),
            ("Systems Engineer programming in C++, Go, Linux kernel concepts, concurrency, multithreading, socket programming, high-performance distributed backend services.", "Backend & Systems Engineering"),
            (".NET Developer building backend microservices with C#, ASP.NET Core, Entity Framework, SQL Server, Azure App Services, dependency injection, unit testing.", "Backend & Systems Engineering"),
            ("Senior Backend Engineer architecting scalable distributed systems, database query optimization, Redis pub/sub, message queuing with RabbitMQ, REST and GraphQL APIs.", "Backend & Systems Engineering"),

            # BI & Analytics
            ("Business Intelligence Analyst skilled in Power BI, Tableau, Advanced Excel, DAX, Power Query, SQL reporting, KPI dashboard design, business analytics, data storytelling.", "Business Intelligence & Analytics"),
            ("Data & BI Specialist translating raw business data into interactive executive dashboards with Tableau and Power BI, financial forecasting, cohort analysis, SQL queries.", "Business Intelligence & Analytics"),
            ("BI Developer designing ETL pipelines for reporting, data modeling in Power BI, complex DAX measures, automated email alerts, stakeholder presentations, Looker reports.", "Business Intelligence & Analytics"),
            ("Business Analyst with expertise in Excel pivot tables, VLOOKUP, Power BI dashboards, requirements gathering, KPI definition, data warehousing concepts, Google Analytics.", "Business Intelligence & Analytics"),
            ("Senior Analytics Consultant creating self-service BI platforms, executive scorecards in Tableau, statistical data validation, revenue attribution models, SQL analytics.", "Business Intelligence & Analytics")
        ]

        return pd.DataFrame(data, columns=["text", "category"])
