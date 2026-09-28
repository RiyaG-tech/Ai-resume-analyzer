"""
Profile Builder & Aggregation Module
Builds structured candidate profiles from PDF resume extraction, manual form inputs,
or a unified hybrid blend (Resume + Manual input).
"""

import re
from typing import Dict, List, Any, Optional
from src.skill_extractor import SkillExtractor, CANONICAL_MAP
from src.entity_extractor import extract_all_entities, extract_years_of_experience
from src.pdf_extractor import extract_text_from_pdf, extract_document


class ProfileBuilder:
    def __init__(self, skill_extractor: SkillExtractor = None):
        self.skill_extractor = skill_extractor or SkillExtractor()

    def build_from_resume(self, file_obj: Any, filename: str = "resume.pdf") -> Dict[str, Any]:
        """
        Extracts content from uploaded PDF/document and builds candidate profile.
        """
        extracted = extract_document(file_obj, filename)
        raw_text = extracted.get('text', '')
        page_count = extracted.get('page_count', 1)
        extractor_used = extracted.get('extractor_used', 'pdfplumber')
        
        # Skill extraction
        skills_data = self.skill_extractor.extract_skills(raw_text)
        
        # Entity extraction
        entities = extract_all_entities(raw_text)

        return {
            'source_mode': 'resume_upload',
            'raw_text': raw_text,
            'page_count': page_count,
            'extractor_used': extractor_used,
            'skills': skills_data['canonical_skills'],
            'skills_by_category': skills_data['skills_by_category'],
            'education': entities['education'],
            'education_details': entities['education_details'],
            'experience': f"{entities['experience_metrics']['estimated_years']} years estimated",
            'experience_years': entities['experience_metrics']['estimated_years'],
            'projects': entities['projects'],
            'certifications': entities['certifications'],
            'quantifiable_achievements': entities['quantifiable_achievements'],
            'action_verbs': entities['action_verbs'],
            'links': entities['links'],
            'interests': [],
            'career_goals': ''
        }

    def build_from_manual(
        self,
        education_degree: str = "",
        branch: str = "",
        manual_skills: List[str] = None,
        experience_text: str = "",
        experience_years: float = 0.0,
        projects_text: str = "",
        certifications_text: str = "",
        interests_text: str = "",
        career_goals: str = ""
    ) -> Dict[str, Any]:
        """
        Builds candidate profile purely from manual input form.
        """
        manual_skills = manual_skills or []
        
        # Parse text fields for skills as well
        combined_text = f"{education_degree} {branch} {' '.join(manual_skills)} {experience_text} {projects_text} {certifications_text} {interests_text} {career_goals}"
        extracted_from_text = self.skill_extractor.extract_skills(combined_text)
        
        # Deduplicate and canonicalize
        all_skills = set(manual_skills)
        for s in extracted_from_text['canonical_skills']:
            all_skills.add(s)

        canonical_skills = sorted(list({CANONICAL_MAP.get(s.lower().strip(), s.strip()) for s in all_skills if s.strip()}))

        # Categorize
        categorized: Dict[str, List[str]] = {}
        for s in canonical_skills:
            cat = self.skill_extractor.skill_to_category.get(s, "Other Key Competencies")
            categorized.setdefault(cat, []).append(s)

        # Parse projects
        projects_list = []
        if projects_text:
            for line in projects_text.split('\n'):
                line_s = line.strip().lstrip('-*• ')
                if len(line_s) > 5:
                    projects_list.append({'title': line_s[:80], 'details': line_s})

        # Parse certifications
        cert_list = []
        if certifications_text:
            for line in certifications_text.split('\n'):
                line_s = line.strip().lstrip('-*• ')
                if len(line_s) > 3:
                    cert_list.append(line_s)

        # Education
        edu_list = []
        if education_degree:
            edu_str = f"{education_degree} in {branch}" if branch else education_degree
            edu_list.append(edu_str)

        return {
            'source_mode': 'manual_input',
            'raw_text': combined_text,
            'page_count': 1,
            'extractor_used': 'manual_form',
            'skills': canonical_skills,
            'skills_by_category': categorized,
            'education': edu_list,
            'education_details': [{'degree': education_degree, 'branch': branch}] if education_degree else [],
            'experience': experience_text or f"{experience_years} years",
            'experience_years': experience_years,
            'projects': projects_list,
            'certifications': cert_list,
            'quantifiable_achievements': [],
            'action_verbs': {'count': 0, 'score': 70, 'unique_action_verbs': []},
            'links': {'linkedin': [], 'github': [], 'portfolio_other': []},
            'interests': [i.strip() for i in interests_text.split(',') if i.strip()] if interests_text else [],
            'career_goals': career_goals
        }

    def combine_profiles(self, resume_profile: Dict[str, Any], manual_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combines Resume profile with Manual Input profile (Option 3).
        Manual information supplements and augments the extracted resume information.
        """
        if not resume_profile and manual_profile:
            return manual_profile
        if not manual_profile and resume_profile:
            return resume_profile
        if not resume_profile and not manual_profile:
            return self.build_from_manual()

        # Combine skills
        combined_skills = set(resume_profile.get('skills', []))
        for s in manual_profile.get('skills', []):
            combined_skills.add(s)

        canonical_skills = sorted(list({CANONICAL_MAP.get(s.lower().strip(), s.strip()) for s in combined_skills if s.strip()}))

        # Categorize
        categorized: Dict[str, List[str]] = {}
        for s in canonical_skills:
            cat = self.skill_extractor.skill_to_category.get(s, "Other Key Competencies")
            categorized.setdefault(cat, []).append(s)

        # Combine education
        combined_education = list(dict.fromkeys(resume_profile.get('education', []) + manual_profile.get('education', [])))
        combined_edu_details = resume_profile.get('education_details', []) + manual_profile.get('education_details', [])

        # Combine experience
        res_exp_yrs = resume_profile.get('experience_years', 0.0)
        man_exp_yrs = manual_profile.get('experience_years', 0.0)
        final_exp_yrs = max(res_exp_yrs, man_exp_yrs)
        
        res_exp_str = resume_profile.get('experience', '')
        man_exp_str = manual_profile.get('experience', '')
        final_exp_str = f"{res_exp_str}; {man_exp_str}".strip('; ') if man_exp_str else res_exp_str

        # Combine projects
        combined_projects = resume_profile.get('projects', []) + manual_profile.get('projects', [])
        # Deduplicate projects by title
        seen_proj = set()
        dedup_projects = []
        for p in combined_projects:
            t = p.get('title', '').lower()
            if t and t not in seen_proj:
                seen_proj.add(t)
                dedup_projects.append(p)

        # Combine certifications
        combined_certs = list(dict.fromkeys(resume_profile.get('certifications', []) + manual_profile.get('certifications', [])))

        # Combined text for TF-IDF
        combined_text = f"{resume_profile.get('raw_text', '')}\n\n{manual_profile.get('raw_text', '')}"

        return {
            'source_mode': 'hybrid_combined',
            'raw_text': combined_text,
            'page_count': resume_profile.get('page_count', 1),
            'extractor_used': f"{resume_profile.get('extractor_used', 'pdf')} + manual_input",
            'skills': canonical_skills,
            'skills_by_category': categorized,
            'education': combined_education,
            'education_details': combined_edu_details,
            'experience': final_exp_str,
            'experience_years': final_exp_yrs,
            'projects': dedup_projects,
            'certifications': combined_certs,
            'quantifiable_achievements': resume_profile.get('quantifiable_achievements', []),
            'action_verbs': resume_profile.get('action_verbs', {'count': 0, 'score': 75, 'unique_action_verbs': []}),
            'links': resume_profile.get('links', {'linkedin': [], 'github': [], 'portfolio_other': []}),
            'interests': manual_profile.get('interests', []),
            'career_goals': manual_profile.get('career_goals', '')
        }
