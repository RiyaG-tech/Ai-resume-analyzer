"""
Recommendation and Resume Audit Engine
Generates targeted skill-gap learning paths, ordered roadmaps, ATS optimization audits,
factual resume strengths, improvement suggestions, and role-specific interview preparation.
"""

from typing import Dict, List, Any
from src.text_cleaner import extract_sections
from src.entity_extractor import extract_all_entities

# Curated certification recommendations by skill/domain
SKILL_CERTIFICATIONS = {
    "AWS": ["AWS Certified Solutions Architect – Associate", "AWS Certified Developer – Associate"],
    "Microsoft Azure": ["Microsoft Certified: Azure Fundamentals (AZ-900)", "Azure Solutions Architect Expert"],
    "Google Cloud (GCP)": ["Google Cloud Associate Cloud Engineer", "Google Professional Cloud Architect"],
    "Kubernetes": ["Certified Kubernetes Administrator (CKA)", "Certified Kubernetes Application Developer (CKAD)"],
    "Docker": ["Docker Certified Associate (DCA)"],
    "Terraform": ["HashiCorp Certified: Terraform Associate"],
    "Python": ["PCEP – Certified Entry-Level Python Programmer", "PCAP – Certified Associate in Python"],
    "Machine Learning": ["DeepLearning.AI Machine Learning Specialization", "TensorFlow Developer Certificate"],
    "Deep Learning": ["DeepLearning.AI Deep Learning Specialization", "Fast.ai Practical Deep Learning"],
    "Natural Language Processing (NLP)": ["DeepLearning.AI Natural Language Processing Specialization", "Hugging Face NLP Course"],
    "Generative AI": ["DeepLearning.AI Generative AI for Everyone", "LangChain & Vector Databases Mastery"],
    "Power BI": ["Microsoft Certified: Power BI Data Analyst Associate (PL-300)"],
    "Tableau": ["Tableau Desktop Specialist", "Tableau Certified Data Analyst"],
    "Cybersecurity": ["CompTIA Security+", "Certified Information Systems Security Professional (CISSP)", "CEH (Certified Ethical Hacker)"],
    "Scrum / Agile": ["Professional Scrum Master (PSM I)", "Certified ScrumMaster (CSM)"],
    "SQL": ["Oracle Certified Database Associate", "Complete SQL Bootcamp (PostgreSQL/MySQL)"],
    "React": ["Meta Front-End Developer Professional Certificate (Coursera)", "Epic React by Kent C. Dodds"],
    "Node.js": ["OpenJS Node.js Application Developer (JSNAD)"],
    "Java": ["Oracle Certified Professional: Java SE Developer"]
}

# Free learning resources & roadmaps
LEARNING_RESOURCES = {
    "Python": "https://docs.python.org/3/tutorial/ and Automate the Boring Stuff with Python",
    "React": "https://react.dev/learn (Official React Documentation)",
    "Node.js": "https://nodejs.org/en/learn (Official Node.js Guide)",
    "Docker": "https://docker-curriculum.com/ and Official Docker Docs",
    "Kubernetes": "https://kubernetes.io/docs/tutorials/ and KodeKloud",
    "AWS": "AWS Skill Builder Free Tier & AWS Free Tier Hands-on Labs",
    "SQL": "https://sqlzoo.net/ and LeetCode SQL 50 Study Plan",
    "Machine Learning": "Scikit-Learn Official User Guide & Fast.ai Practical Deep Learning",
    "Deep Learning": "DeepLearning.AI Coursera & PyTorch Official 60-Minute Blitz",
    "PyTorch": "https://pytorch.org/tutorials/ (Official PyTorch Tutorials)",
    "TensorFlow": "https://www.tensorflow.org/tutorials",
    "FastAPI": "https://fastapi.tiangolo.com/tutorial/ (Interactive FastAPI Docs)",
    "Git": "https://git-scm.com/book/en/v2 (Pro Git Book)",
    "Power BI": "Microsoft Learn: Power BI Guided Learning Paths",
    "Tableau": "Tableau Free Training Videos & Tableau Public community"
}

# Learning difficulty / foundational hierarchy for sequencing
SKILL_PRIORITY_ORDER = {
    "Programming Fundamentals": 1,
    "Python": 1, "Java": 1, "C++": 1, "JavaScript": 1, "SQL": 1, "HTML": 1, "CSS": 1, "Git": 1,
    "Data Structures": 2, "Algorithms": 2, "Pandas": 2, "NumPy": 2, "React": 2, "Node.js": 2,
    "Machine Learning": 3, "Scikit-Learn": 3, "Statistical Analysis": 3, "REST API": 3, "PostgreSQL": 3, "MongoDB": 3,
    "Deep Learning": 4, "PyTorch": 4, "TensorFlow": 4, "Docker": 4, "FastAPI": 4, "Linux": 4, "Power BI": 4,
    "Natural Language Processing (NLP)": 5, "Computer Vision": 5, "Kubernetes": 5, "AWS": 5, "Azure": 5, "CI/CD": 5, "Terraform": 5,
    "Generative AI": 6, "LLMs": 6, "RAG (Retrieval-Augmented Generation)": 6, "MLOps": 6
}


class RecommendationEngine:
    def __init__(self):
        pass

    def generate_resume_strengths(self, user_profile: Dict[str, Any]) -> List[str]:
        """
        Identifies factual strengths based on actual information detected.
        Does not invent or assume unsubstantiated data.
        """
        strengths = []
        skills = user_profile.get('skills', [])
        projects = user_profile.get('projects', [])
        experience = user_profile.get('experience', '')
        exp_years = user_profile.get('experience_years', 0.0)
        education = user_profile.get('education', [])
        certifications = user_profile.get('certifications', [])
        quantifiable = user_profile.get('quantifiable_achievements', [])
        
        # Skill-based strengths
        has_python = any('python' in s.lower() for s in skills)
        has_sql = any('sql' in s.lower() for s in skills)
        has_ml = any('machine learning' in s.lower() or 'scikit-learn' in s.lower() for s in skills)
        has_dl = any('deep learning' in s.lower() or 'pytorch' in s.lower() or 'tensorflow' in s.lower() for s in skills)
        has_web = any('react' in s.lower() or 'node.js' in s.lower() or 'javascript' in s.lower() for s in skills)
        has_cloud = any('aws' in s.lower() or 'docker' in s.lower() or 'kubernetes' in s.lower() or 'azure' in s.lower() for s in skills)

        if has_python and has_sql:
            strengths.append("✓ Strong dual core in Python and SQL (essential for high-impact analytical & engineering roles).")
        elif has_python:
            strengths.append("✓ Solid Python programming foundation detected across the profile.")
        elif has_sql:
            strengths.append("✓ Relational database querying and SQL competency demonstrated.")

        if has_ml and has_dl:
            strengths.append("✓ Comprehensive Machine Learning and Deep Learning skillset identified.")
        elif has_ml:
            strengths.append("✓ Practical Machine Learning and statistical modeling competencies detected.")

        if has_web:
            strengths.append("✓ Modern web application and full-stack development experience present.")

        if has_cloud:
            strengths.append("✓ Cloud infrastructure, containerization, or DevOps capabilities identified.")

        # Project strengths
        if len(projects) >= 2:
            strengths.append(f"✓ Multiple technical projects ({len(projects)}+ projects) demonstrating hands-on implementation.")
        elif len(projects) == 1:
            strengths.append("✓ Hands-on project implementation present in profile.")

        # Experience strengths
        if exp_years > 0 or (isinstance(experience, str) and len(experience.strip()) > 15):
            strengths.append(f"✓ Demonstrable professional/internship experience ({exp_years if exp_years > 0 else 'Active'} duration).")

        # Certification strengths
        if certifications and len(certifications) > 0:
            strengths.append(f"✓ Verified certifications ({len(certifications)} credential(s)) demonstrating continuous upskilling.")

        # Quantifiable metrics strength
        if len(quantifiable) >= 2:
            strengths.append(f"✓ Results-oriented phrasing with quantifiable business/technical impact ({len(quantifiable)} metrics found).")

        # Education
        if education and len(education) > 0:
            edu_str = education[0] if isinstance(education[0], str) else education[0].get('degree', 'Technical Degree')
            strengths.append(f"✓ Solid academic background ({edu_str}).")

        if not strengths:
            strengths.append("✓ Clean baseline profile ready for targeted skill enhancement and portfolio additions.")

        return strengths

    def generate_resume_improvements(
        self,
        user_profile: Dict[str, Any],
        missing_skills: List[str],
        target_role: str = ""
    ) -> List[Dict[str, str]]:
        """
        Generates grounded, non-inventive resume improvement suggestions.
        """
        suggestions = []
        quantifiable = user_profile.get('quantifiable_achievements', [])
        projects = user_profile.get('projects', [])
        certifications = user_profile.get('certifications', [])
        action_verbs = user_profile.get('action_verbs', {})
        skills = user_profile.get('skills', [])

        # 1. Quantifiable metrics
        if len(quantifiable) < 3:
            suggestions.append({
                'category': 'Impact & Metrics',
                'action': 'Add measurable project outcomes.',
                'details': 'Incorporate concrete performance numbers, latency reductions, or accuracy improvements (e.g., "Improved query execution speed by 35%" or "Achieved 92% classification F1-score").'
            })

        # 2. Tech highlight in projects
        suggestions.append({
            'category': 'Technical Clarity',
            'action': 'Highlight relevant technologies in each project.',
            'details': 'List the exact tools, libraries, and frameworks utilized right under each project title (e.g., "Tech Stack: Python, FastAPI, PostgreSQL, Docker").'
        })

        # 3. Project descriptions
        if len(projects) > 0:
            suggestions.append({
                'category': 'Project Structure',
                'action': 'Improve descriptions of projects using the XYZ action format.',
                'details': 'Structure bullet points as: Accomplished [X], as measured by [Y], by doing [Z] to show both engineering depth and business impact.'
            })

        # 4. Certifications
        if not certifications:
            suggestions.append({
                'category': 'Credentials',
                'action': 'Add relevant certifications.',
                'details': f'Earn and display recognized credentials relevant to {target_role or "your target career path"} to validate your expertise.'
            })

        # 5. Technical skills visibility
        suggestions.append({
            'category': 'ATS Formatting',
            'action': 'Make important technical skills easier to identify.',
            'details': 'Organize skills into clean categories (Languages, Frameworks, Developer Tools, Databases) so recruiters and ATS parsers scan them immediately.'
        })

        # 6. Missing skills advisory (strictly compliant with safety rule)
        if missing_skills:
            top_missing = ", ".join(missing_skills[:4])
            suggestions.append({
                'category': 'Skill Alignment',
                'action': 'Add missing skills only if you actually possess them.',
                'details': f'For target role "{target_role}", key skills include {top_missing}. If you have worked with these, ensure they are explicitly named on your resume; otherwise, focus on learning them.'
            })

        return suggestions

    def generate_ordered_learning_roadmap(self, missing_skills: List[str]) -> List[Dict[str, Any]]:
        """
        Orders missing skills into a logical pedagogical learning sequence.
        """
        # Sort by predefined priority order
        sorted_skills = sorted(
            missing_skills,
            key=lambda s: SKILL_PRIORITY_ORDER.get(s, 10)
        )

        roadmap = []
        for idx, skill in enumerate(sorted_skills[:8], start=1):
            cert_list = SKILL_CERTIFICATIONS.get(skill, [f"Industry-recognized course on {skill} (Coursera / Udemy)"])
            resource = LEARNING_RESOURCES.get(skill, f"Official {skill} Documentation and community hands-on tutorials")
            priority = "High" if SKILL_PRIORITY_ORDER.get(skill, 10) <= 3 else "Medium"
            
            roadmap.append({
                'order': idx,
                'skill': skill,
                'priority': priority,
                'certifications': cert_list,
                'resource': resource,
                'suggested_project': f"Build a practical mini-project integrating {skill}."
            })
        return roadmap

    def audit_resume_ats(self, resume_text: str) -> Dict[str, Any]:
        """
        Performs comprehensive ATS check.
        """
        entities = extract_all_entities(resume_text)
        sections = extract_sections(resume_text)
        
        words = resume_text.split()
        word_count = len(words)

        if 350 <= word_count <= 900:
            length_status = "Optimal"
            length_score = 100
            length_tip = f"Word count ({word_count} words) is well-balanced for ATS parsers and recruiters."
        elif word_count < 350:
            length_status = "Brief"
            length_score = 65
            length_tip = f"Resume is brief ({word_count} words). Consider adding more details on project implementations."
        else:
            length_status = "Lengthy"
            length_score = 75
            length_tip = f"Resume is lengthy ({word_count} words). Consolidate older bullets to keep it concise."

        critical_sections = ['summary', 'experience', 'education', 'skills', 'projects']
        found_sections = [sec for sec in critical_sections if len(sections.get(sec, '')) > 20]
        missing_sections = [sec.title() for sec in critical_sections if sec not in found_sections]
        section_score = int((len(found_sections) / len(critical_sections)) * 100)

        action_verbs_data = entities['action_verbs']
        verbs_score = action_verbs_data['score']

        quantifiable = entities['quantifiable_achievements']
        quant_score = min(100, len(quantifiable) * 20)

        overall_ats_score = int(
            (0.30 * section_score) +
            (0.25 * verbs_score) +
            (0.25 * quant_score) +
            (0.20 * length_score)
        )

        return {
            'overall_ats_score': overall_ats_score,
            'word_count': word_count,
            'length_status': length_status,
            'length_tip': length_tip,
            'sections_found': [s.title() for s in found_sections],
            'sections_missing': missing_sections,
            'section_score': section_score,
            'action_verbs_count': action_verbs_data['count'],
            'action_verbs_score': verbs_score,
            'quantifiable_metrics_count': len(quantifiable),
            'quantifiable_metrics_samples': quantifiable,
            'quantifiable_score': quant_score
        }
