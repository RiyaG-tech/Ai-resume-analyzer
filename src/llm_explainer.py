"""
Optional LLM Explanation Layer Module
Provides AI-powered executive feedback, tailored resume rewrite tips, and interview coaching.
Integrates with Google Gemini API if an API key is available; otherwise gracefully falls back
to intelligent rule-based heuristic explanations.
"""

import os
from typing import Dict, Any, Optional

try:
    from google import genai
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False


class LLMExplainer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key and HAS_GOOGLE_GENAI:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def is_available(self) -> bool:
        """Returns True if a valid LLM client is configured."""
        return self.client is not None

    def generate_ai_analysis(
        self,
        resume_text: str,
        jd_text: str,
        match_data: Dict[str, Any],
        predicted_role: str
    ) -> Dict[str, str]:
        """
        Generates executive summary, bullet point rewriting tips, and hiring manager perspective.
        Uses Gemini API if key is present; otherwise falls back to smart rule-based insights.
        """
        if self.is_available():
            try:
                return self._generate_gemini_insights(resume_text, jd_text, match_data, predicted_role)
            except Exception as e:
                # Graceful fallback on API error or quota limit
                fallback = self._generate_heuristic_insights(match_data, predicted_role)
                fallback['notice'] = f"LLM API request failed ({str(e)[:60]}). Showing rule-based smart insights."
                return fallback
        else:
            return self._generate_heuristic_insights(match_data, predicted_role)

    def _generate_gemini_insights(
        self,
        resume_text: str,
        jd_text: str,
        match_data: Dict[str, Any],
        predicted_role: str
    ) -> Dict[str, str]:
        """Calls Google Gemini API for tailored feedback."""
        score = match_data.get('overall_score', 0)
        matched_skills = ", ".join(match_data.get('skills_analysis', {}).get('matched_skills', [])[:10])
        missing_skills = ", ".join(match_data.get('skills_analysis', {}).get('missing_skills', [])[:10])

        prompt = f"""
You are an expert Executive Technical Recruiter and Career Coach.
Analyze this candidate match:

- Overall Match Score: {score}%
- Predicted Domain: {predicted_role}
- Matched Skills: {matched_skills or 'None'}
- Missing Skills: {missing_skills or 'None'}

Resume Excerpt:
{resume_text[:1200]}

Target Job Description Excerpt:
{jd_text[:1200]}

Provide a structured evaluation in concise Markdown format with these exact headings:
### 1. Executive Summary & Verdict
(Brief assessment of fit and competitive standing)

### 2. Top Strengths for this Specific Role
(2-3 bullet points on standout qualifications)

### 3. Critical Gaps to Address
(Specific actionable steps to overcome missing competencies)

### 4. Tailored Resume Bullet Rewrites
(Take 1-2 generic bullet points from the resume and rewrite them into high-impact, quantified achievement statements relevant to the JD)

### 5. Hiring Manager's Likely Questions
(2 realistic interview questions the hiring manager will ask)
"""

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        return {
            'analysis': response.text,
            'source': 'Google Gemini AI (gemini-2.5-flash)',
            'status': 'success'
        }

    def _generate_heuristic_insights(
        self,
        match_data: Dict[str, Any],
        predicted_role: str
    ) -> Dict[str, str]:
        """
        Smart template-based analysis generator requiring NO external API key.
        Ensures the system is 100% self-sufficient offline.
        """
        score = match_data.get('overall_score', 0)
        skills_info = match_data.get('skills_analysis', {})
        matched = skills_info.get('matched_skills', [])
        missing = skills_info.get('missing_skills', [])
        additional = skills_info.get('additional_skills', [])

        # Format matched skills
        matched_str = ", ".join(matched[:6]) if matched else "General software fundamentals"
        missing_str = ", ".join(missing[:6]) if missing else "No critical technical gaps identified"
        extra_str = ", ".join(additional[:5]) if additional else "None noted"

        if score >= 80:
            summary = (
                f"The candidate demonstrates strong technical alignment for the **{predicted_role}** target role "
                f"with an overall score of **{score}%**. Core competencies in **{matched_str}** directly meet "
                "the primary job specifications."
            )
        elif score >= 60:
            summary = (
                f"The candidate possesses a solid foundation for **{predicted_role}** with an overall score of **{score}%**. "
                f"Strengths include **{matched_str}**, but key gaps in **{missing_str}** should be addressed before final interviews."
            )
        else:
            summary = (
                f"The candidate's profile shows a noticeable divergence from the job requirements (Match Score: **{score}%**). "
                f"While possessing skills like **{matched_str}**, critical required proficiencies such as **{missing_str}** are absent."
            )

        analysis_md = f"""
### 1. Executive Summary & Verdict
{summary}

### 2. Top Strengths for this Specific Role
- **Matching Core Tech Stack:** Strong overlap in required technologies: **{matched_str}**.
- **Versatility / Bonus Skills:** Possesses additional capabilities in **{extra_str}**, which can add cross-functional value to the team.
- **Domain Alignment:** High confidence match with the **{predicted_role}** career track.

### 3. Critical Gaps to Address
- **Priority Competencies:** Focus on acquiring practical experience in **{missing_str}**.
- **Portfolio Proof:** Build and deploy a public demo on GitHub demonstrating these missing technologies.
- **Keyword Integration:** Ensure relevant technical keywords appear naturally in project descriptions.

### 4. Tailored Resume Bullet Rewriting Strategy
- **Standard Bullet:** *"Worked on web application development using React and backend APIs."*
- **High-Impact Rewrite:** *"Architected and deployed responsive full-stack features using {matched[:2] if matched else 'modern frameworks'}, improving user task completion speed by 25%."*
- **Action Rule:** Always follow the Google XYZ formula: *Accomplished [X] as measured by [Y], by doing [Z]*.

### 5. Hiring Manager's Likely Questions
1. *"Can you walk us through how you applied {matched[0] if matched else 'core tools'} in a production environment?"*
2. *"The role relies heavily on {missing[0] if missing else 'system architecture'}. How would you bridge your familiarity with this technology in your first 30 days?"*
"""

        return {
            'analysis': analysis_md.strip(),
            'source': 'Built-in Intelligent Rule Engine (Offline Mode)',
            'status': 'offline_success'
        }
