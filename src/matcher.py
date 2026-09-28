"""
Core Matching Engine Module
Computes TF-IDF vector representations, Cosine Similarity, Skill Overlap,
and a Multi-Factor Weighted Hybrid Job Match Score.
Supports both custom Job Descriptions and curated Career Role Taxonomies.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.text_cleaner import clean_for_nlp
from src.skill_extractor import SkillExtractor, CANONICAL_MAP
from src.entity_extractor import extract_years_of_experience, extract_education
from src.career_roles import CAREER_ROLES, get_role_details


class JobMatcher:
    def __init__(self, skill_extractor: SkillExtractor = None):
        self.skill_extractor = skill_extractor or SkillExtractor()

    def compute_tfidf_similarity(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Computes TF-IDF vectors using unigrams and bigrams, and calculates Cosine Similarity.
        Also extracts top shared n-gram keywords that drove the similarity.
        """
        clean_resume = clean_for_nlp(resume_text)
        clean_jd = clean_for_nlp(jd_text)

        if not clean_resume or not clean_jd:
            return {
                'cosine_similarity': 0.0,
                'top_common_keywords': [],
                'tfidf_matrix_shape': (0, 0)
            }

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=5000
        )

        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        score_percent = round(sim * 100, 2)

        feature_names = np.array(vectorizer.get_feature_names_out())
        resume_vec = tfidf_matrix[0].toarray().flatten()
        jd_vec = tfidf_matrix[1].toarray().flatten()

        shared_importance = resume_vec * jd_vec
        top_indices = shared_importance.argsort()[::-1]

        top_keywords = []
        for idx in top_indices:
            if shared_importance[idx] > 0:
                top_keywords.append({
                    'keyword': feature_names[idx],
                    'importance_score': round(float(shared_importance[idx]) * 100, 3),
                    'resume_weight': round(float(resume_vec[idx]), 3),
                    'jd_weight': round(float(jd_vec[idx]), 3)
                })
            if len(top_keywords) >= 15:
                break

        return {
            'cosine_similarity': score_percent,
            'raw_cosine': sim,
            'top_common_keywords': top_keywords,
            'tfidf_matrix_shape': tfidf_matrix.shape
        }

    def match_profile_against_roles(
        self,
        user_skills: List[str],
        profile_text: str = "",
        experience_years: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Matches a user's extracted/entered skills and profile against all predefined career roles.
        Calculates similarity scores, matched skills, missing skills, and ranking.
        """
        # Canonicalize user skills
        canonical_user_skills = set()
        for s in user_skills:
            s_clean = s.strip()
            canonical = CANONICAL_MAP.get(s_clean.lower(), s_clean)
            canonical_user_skills.add(canonical)
            canonical_user_skills.add(s_clean)  # keep both for fuzzy overlap

        results = []
        for role_name, role_info in CAREER_ROLES.items():
            core_req = set(role_info.get('required_core_skills', []))
            sec_req = set(role_info.get('secondary_skills', []))
            all_req = core_req.union(sec_req)

            # Check overlap case-insensitively
            user_skills_lower = {s.lower() for s in canonical_user_skills}
            
            matched_core = [s for s in core_req if s.lower() in user_skills_lower]
            matched_sec = [s for s in sec_req if s.lower() in user_skills_lower]
            
            matched_skills = sorted(list(set(matched_core + matched_sec)))
            missing_skills = sorted([s for s in all_req if s.lower() not in user_skills_lower])

            # Weighted skill match score
            core_score = (len(matched_core) / len(core_req) * 100) if core_req else 100.0
            sec_score = (len(matched_sec) / len(sec_req) * 100) if sec_req else 100.0
            skill_score = (0.75 * core_score) + (0.25 * sec_score)

            # TF-IDF text similarity component if profile text is available
            role_text = f"{role_name} {role_info.get('description', '')} {' '.join(all_req)}"
            if profile_text and len(profile_text.split()) >= 10:
                tfidf_res = self.compute_tfidf_similarity(profile_text, role_text)
                tfidf_score = tfidf_res['cosine_similarity']
                # Hybrid match
                overall_score = (0.65 * skill_score) + (0.35 * tfidf_score)
            else:
                overall_score = skill_score

            # Scale and round
            overall_score = round(min(99.0, max(12.0 if matched_skills else 5.0, overall_score)), 1)

            results.append({
                'role': role_name,
                'category': role_info.get('category', 'Technology'),
                'description': role_info.get('description', ''),
                'match_percentage': overall_score,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'required_core_skills': list(core_req),
                'secondary_skills': list(sec_req),
                'core_match_count': f"{len(matched_core)}/{len(core_req)}",
                'total_matched_count': len(matched_skills),
                'total_required_count': len(all_req)
            })

        # Sort by match percentage descending
        results.sort(key=lambda x: x['match_percentage'], reverse=True)
        return results

    def calculate_hybrid_match(
        self,
        resume_text: str,
        jd_text: str,
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Main calculation orchestrator that produces the holistic Job Match Score for a custom JD.
        """
        if weights is None:
            weights = {
                'skills': 0.45,
                'tfidf': 0.35,
                'experience': 0.10,
                'education': 0.10
            }

        skill_res = self.skill_extractor.compare_skills(resume_text, jd_text)
        skill_score = skill_res['match_percentage']

        tfidf_res = self.compute_tfidf_similarity(resume_text, jd_text)
        tfidf_score = tfidf_res['cosine_similarity']

        exp_res = self.compute_experience_alignment(resume_text, jd_text)
        exp_score = exp_res['experience_score']

        edu_res = self.compute_education_alignment(resume_text, jd_text)
        edu_score = edu_res['education_score']

        final_score = (
            (weights['skills'] * skill_score) +
            (weights['tfidf'] * tfidf_score) +
            (weights['experience'] * exp_score) +
            (weights['education'] * edu_score)
        )
        final_score = round(min(100.0, max(0.0, final_score)), 1)

        if final_score >= 85:
            match_tier = "Excellent Match"
            tier_color = "#10B981"
            verdict = "Strong candidate profile. Highly recommended for interview screening."
        elif final_score >= 70:
            match_tier = "Good Match"
            tier_color = "#3B82F6"
            verdict = "Solid alignment with key requirements with minor skill gaps to address."
        elif final_score >= 50:
            match_tier = "Moderate Match"
            tier_color = "#F59E0B"
            verdict = "Partial match. Notable skill or experience gaps need bridging."
        else:
            match_tier = "Low Match"
            tier_color = "#EF4444"
            verdict = "Significant mismatch in core competencies or required tech stack."

        return {
            'overall_score': final_score,
            'match_tier': match_tier,
            'tier_color': tier_color,
            'verdict': verdict,
            'score_breakdown': {
                'skill_match_score': skill_score,
                'tfidf_cosine_score': tfidf_score,
                'experience_score': exp_score,
                'education_score': edu_score,
                'weights': weights
            },
            'skills_analysis': skill_res,
            'tfidf_analysis': tfidf_res,
            'experience_analysis': exp_res,
            'education_analysis': edu_res
        }

    def compute_experience_alignment(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        res_exp = extract_years_of_experience(resume_text)
        jd_exp = extract_years_of_experience(jd_text)

        res_years = res_exp['estimated_years']
        jd_years = jd_exp['estimated_years']

        if jd_years == 0:
            exp_score = 100.0
            status = "No specific minimum years strictly required"
        elif res_years >= jd_years:
            exp_score = 100.0
            status = f"Fully meets experience requirement ({res_years} yrs vs {jd_years} yrs required)"
        else:
            ratio = (res_years / jd_years)
            exp_score = round(max(30.0, ratio * 100), 1)
            status = f"Below preferred experience ({res_years} yrs vs {jd_years} yrs required)"

        return {
            'resume_years': res_years,
            'jd_required_years': jd_years,
            'experience_score': exp_score,
            'status': status
        }

    def compute_education_alignment(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        res_edu = extract_education(resume_text)
        jd_edu = extract_education(jd_text)

        edu_hierarchy = {
            'Ph.D. / Doctorate': 5,
            "Master's Degree": 4,
            "Bachelor's Degree": 3,
            'Associate / Diploma': 2,
            'High School': 1
        }

        res_max_level = max([edu_hierarchy.get(e.split(' ')[0], 0) for e in res_edu], default=3)
        jd_max_level = max([edu_hierarchy.get(e.split(' ')[0], 0) for e in jd_edu], default=3)

        if not jd_edu:
            edu_score = 100.0
            status = "Standard degree requirement assumed satisfied"
        elif res_max_level >= jd_max_level:
            edu_score = 100.0
            status = f"Degree requirement fully satisfied ({', '.join(res_edu) or 'Bachelor'})"
        else:
            edu_score = 75.0
            status = f"Candidate holds {', '.join(res_edu) or 'Equivalent degree'} (JD preferred higher level)"

        return {
            'resume_education': res_edu,
            'jd_education': jd_edu,
            'education_score': edu_score,
            'status': status
        }
