"""
Skill Extraction and Taxonomy Mapping Module
Extracts technical and soft skills using boundary-safe regex, alias resolution, and category tagging.
"""

import json
import os
import re
from typing import Dict, List, Set, Tuple, Any

# Map synonyms / aliases to canonical display names
CANONICAL_MAP = {
    "python": "Python",
    "sql": "SQL",
    "nosql": "NoSQL",
    "mysql": "MySQL",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "streamlit": "Streamlit",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "catboost": "CatBoost",
    "mlflow": "MLflow",
    "dvc": "DVC",
    "docker": "Docker",
    "bert": "BERT",
    "gpt": "GPT",
    "optuna": "Optuna",
    "html": "HTML",
    "html5": "HTML5",
    "css": "CSS",
    "css3": "CSS3",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react.js": "React",
    "reactjs": "React",
    "react": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "vue": "Vue.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "express.js": "Express",
    "express": "Express",
    "angularjs": "Angular",
    "angular": "Angular",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud (GCP)",
    "google cloud platform": "Google Cloud (GCP)",
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "tableau": "Tableau",
    "pyspark": "PySpark",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "nlp": "Natural Language Processing (NLP)",
    "natural language processing": "Natural Language Processing (NLP)",
    "generative ai": "Generative AI",
    "genai": "Generative AI",
    "large language models": "LLMs",
    "llm": "LLMs",
    "rag": "RAG (Retrieval-Augmented Generation)",
    "retrieval augmented generation": "RAG (Retrieval-Augmented Generation)",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "sql server": "MS SQL Server",
    "ms sql": "MS SQL Server",
    "ci/cd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous deployment": "CI/CD",
    "ui/ux": "UI/UX Design",
    "ui design": "UI Design",
    "ux design": "UX Design",
    "c++": "C++",
    "c#": "C#",
    ".net": ".NET",
    ".net core": ".NET Core",
    "asp.net": "ASP.NET",
    "asp.net core": "ASP.NET Core",
    "golang": "Go",
    "go": "Go",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab"
}


class SkillExtractor:
    def __init__(self, dataset_path: str = None):
        if not dataset_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dataset_path = os.path.join(base_dir, "data", "skills_dataset.json")

        self.dataset_path = dataset_path
        self.skills_by_category: Dict[str, List[str]] = {}
        self.skill_to_category: Dict[str, str] = {}
        self.skill_patterns: List[Tuple[str, re.Pattern, str, str]] = [] # (raw_skill, regex, canonical, category)
        self.load_skills()

    def load_skills(self):
        """Loads skills taxonomy from JSON and compiles regex matchers."""
        if os.path.exists(self.dataset_path):
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                self.skills_by_category = json.load(f)
        else:
            # Fallback basic skills if file not found
            self.skills_by_category = {
                "Programming Languages": ["python", "java", "c++", "c#", "javascript", "typescript", "go", "ruby", "sql"],
                "Web & Backend": ["react", "node.js", "django", "flask", "fastapi", "spring boot", "express", "html", "css"],
                "Data Science & ML": ["machine learning", "deep learning", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "nlp", "llm"],
                "Cloud & DevOps": ["aws", "azure", "docker", "kubernetes", "ci/cd", "linux", "git", "terraform"],
                "Databases": ["mysql", "postgresql", "mongodb", "redis", "elasticsearch"]
            }

        patterns = []
        # Sort skills by length descending to match multi-word phrases before single words (e.g. "machine learning" before "learning")
        all_skills_tuples = []
        for category, skills in self.skills_by_category.items():
            for skill in skills:
                skill_lower = skill.lower().strip()
                canonical = CANONICAL_MAP.get(skill_lower, skill.title())
                self.skill_to_category[canonical] = category
                all_skills_tuples.append((skill_lower, canonical, category))

        # Sort longest phrase first
        all_skills_tuples.sort(key=lambda x: len(x[0]), reverse=True)

        for skill_lower, canonical, category in all_skills_tuples:
            # Escape regex special chars except + and #
            escaped = re.escape(skill_lower)
            if skill_lower in ["c++", "c#", ".net"]:
                if skill_lower == "c++":
                    pattern = re.compile(r'(?i)(?:\b|(?<=\s))c\+\+(?=\s|[,\.;:\)]|$)', re.IGNORECASE)
                elif skill_lower == "c#":
                    pattern = re.compile(r'(?i)(?:\b|(?<=\s))c\#(?=\s|[,\.;:\)]|$)', re.IGNORECASE)
                elif skill_lower == ".net":
                    pattern = re.compile(r'(?i)(?:\b|(?<=\s))\.(?:net)(?=\s|[,\.;:\)]|$)', re.IGNORECASE)
            elif skill_lower in ["r", "c", "go"]:
                # Single letter or very short keywords require strict word boundaries and context checks
                pattern = re.compile(rf'(?i)(?:\b|(?<=\s)){escaped}(?=\b|[,\.;:\)])', re.IGNORECASE)
            else:
                pattern = re.compile(rf'(?i)\b{escaped}\b', re.IGNORECASE)

            patterns.append((skill_lower, pattern, canonical, category))

        self.skill_patterns = patterns

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extracts all recognized skills from given text.
        Returns:
            {
                'canonical_skills': List[str],      # Unique canonical names (e.g., ["Python", "React", "AWS"])
                'skills_by_category': Dict[str, List[str]], # Grouped by category
                'raw_matches': Set[str],
                'count': int
            }
        """
        if not text:
            return {'canonical_skills': [], 'skills_by_category': {}, 'raw_matches': set(), 'count': 0}

        # Normalize text lightly
        text_to_search = " " + text.replace("\n", " ").replace("/", " / ") + " "

        detected_canonical = set()
        detected_raw = set()
        categorized: Dict[str, List[str]] = {}

        for raw_skill, regex, canonical, category in self.skill_patterns:
            # Special filter for 'c' and 'r' to avoid single letter false positives
            if raw_skill in ['c', 'r', 'go']:
                matches = regex.findall(text_to_search)
                if matches:
                    # Verify context if possible (e.g., 'C programming', 'language R', 'C/C++')
                    if raw_skill == 'c' and not re.search(r'(?i)\b(c\s*(?:language|programming|\/c\+\+|embedded)|c,\s*c\+\+)', text_to_search):
                        continue
                    if raw_skill == 'r' and not re.search(r'(?i)\b(r\s*(?:programming|language|package|studio|scripting)|using\s*r\b)', text_to_search):
                        continue
                    detected_canonical.add(canonical)
                    detected_raw.add(raw_skill)
                    categorized.setdefault(category, []).append(canonical)
            else:
                if regex.search(text_to_search):
                    detected_canonical.add(canonical)
                    detected_raw.add(raw_skill)
                    if category not in categorized:
                        categorized[category] = []
                    if canonical not in categorized[category]:
                        categorized[category].append(canonical)

        # Sort categorized lists
        for cat in categorized:
            categorized[cat].sort()

        sorted_canonical = sorted(list(detected_canonical))

        return {
            'canonical_skills': sorted_canonical,
            'skills_by_category': categorized,
            'raw_matches': detected_raw,
            'count': len(sorted_canonical)
        }

    def compare_skills(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Compares skills present in Resume vs Job Description.
        Returns:
            - matched_skills: Skills required by JD and present in Resume
            - missing_skills: Skills required by JD but missing in Resume
            - additional_skills: Skills present in Resume but not required by JD
            - match_percentage: Overlap ratio (matched / total_jd_skills)
            - category_breakdown: Breakdown of match per category
        """
        resume_data = self.extract_skills(resume_text)
        jd_data = self.extract_skills(jd_text)

        resume_skills = set(resume_data['canonical_skills'])
        jd_skills = set(jd_data['canonical_skills'])

        matched = sorted(list(resume_skills.intersection(jd_skills)))
        missing = sorted(list(jd_skills - resume_skills))
        additional = sorted(list(resume_skills - jd_skills))

        total_jd = len(jd_skills)
        match_percentage = round((len(matched) / total_jd * 100), 2) if total_jd > 0 else 100.0

        # Category breakdown
        category_breakdown = {}
        all_categories = set(list(resume_data['skills_by_category'].keys()) + list(jd_data['skills_by_category'].keys()))
        for cat in sorted(all_categories):
            r_cat = set(resume_data['skills_by_category'].get(cat, []))
            j_cat = set(jd_data['skills_by_category'].get(cat, []))
            m_cat = list(r_cat.intersection(j_cat))
            miss_cat = list(j_cat - r_cat)
            category_breakdown[cat] = {
                'required': sorted(list(j_cat)),
                'matched': sorted(m_cat),
                'missing': sorted(miss_cat),
                'total_required': len(j_cat),
                'total_matched': len(m_cat),
                'score': round((len(m_cat) / len(j_cat) * 100), 1) if len(j_cat) > 0 else 100.0
            }

        return {
            'resume_skills': resume_data['canonical_skills'],
            'jd_skills': jd_data['canonical_skills'],
            'matched_skills': matched,
            'missing_skills': missing,
            'additional_skills': additional,
            'match_percentage': match_percentage,
            'total_jd_skills': total_jd,
            'total_resume_skills': len(resume_skills),
            'category_breakdown': category_breakdown,
            'resume_by_category': resume_data['skills_by_category'],
            'jd_by_category': jd_data['skills_by_category']
        }
