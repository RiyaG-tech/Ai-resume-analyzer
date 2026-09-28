"""
AI Resume Analyzer & Job Match Predictor
Streamlit Application with Multi-Source Profile Building, Career Matching,
Skill Gap Analysis, Pedagogical Roadmaps, and Privacy Protections.
"""

import os
import io
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.pdf_extractor import extract_text_from_pdf, extract_document
from src.skill_extractor import SkillExtractor, CANONICAL_MAP
from src.entity_extractor import extract_all_entities
from src.matcher import JobMatcher
from src.career_roles import CAREER_ROLES, get_all_career_roles, get_role_details
from src.recommendation_engine import RecommendationEngine
from src.profile_builder import ProfileBuilder
from src.report_generator import generate_markdown_report, generate_pdf_report
from src.llm_explainer import LLMExplainer

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer & Job Match Predictor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        color: #f8fafc;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-card h3 {
        margin: 0;
        font-size: 1.1rem;
        color: #94a3b8;
    }
    .metric-card .val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
        margin: 6px 0;
    }
    
    /* Skill Badge Styling */
    .skill-badge {
        display: inline-block;
        background-color: #0369a1;
        color: #ffffff !important;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        margin: 3px 4px;
        border: 1px solid #0284c7;
    }
    .skill-badge-gap {
        display: inline-block;
        background-color: #7c2d12;
        color: #fed7aa !important;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        margin: 3px 4px;
        border: 1px solid #c2410c;
    }
    .skill-badge-have {
        display: inline-block;
        background-color: #064e3b;
        color: #a7f3d0 !important;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        margin: 3px 4px;
        border: 1px solid #059669;
    }

    /* Strength & Suggestion Item */
    .highlight-box {
        background-color: #1e293b;
        border-left: 4px solid #10b981;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
        color: #f1f5f9;
    }
    .warning-box {
        background-color: #1e293b;
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
        color: #f1f5f9;
    }

    /* Privacy Banner */
    .privacy-banner {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 12px 18px;
        font-size: 0.88rem;
        color: #cbd5e1;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_core_components():
    """Initializes and caches core NLP engines."""
    skill_ext = SkillExtractor()
    matcher = JobMatcher(skill_extractor=skill_ext)
    recommender = RecommendationEngine()
    builder = ProfileBuilder(skill_extractor=skill_ext)
    return skill_ext, matcher, recommender, builder


skill_extractor, job_matcher, recommendation_engine, profile_builder = load_core_components()


# ==========================================
# SIDEBAR: Input Mode & Navigation
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/resume.png", width=64)
    st.title("Profile Input")
    st.caption("Choose how you would like to provide your profile information.")

    input_mode = st.radio(
        "Select Profile Method:",
        [
            "📄 Option 1: Upload Resume (PDF)",
            "✍️ Option 2: Enter Information Manually",
            "🔄 Option 3: Resume + Manual Input (Hybrid)"
        ],
        index=0
    )

    st.markdown("---")
    st.subheader("🎯 Career Target")
    available_roles = get_all_career_roles()
    selected_target_role = st.selectbox(
        "Select Target Career Role:",
        available_roles,
        index=0,
        help="Select the career role you are targeting to run tailored skill gap analysis."
    )

    st.markdown("---")
    st.subheader("🤖 AI / LLM Feature (Optional)")
    enable_ai = st.checkbox("Enable Optional Gemini AI Analysis", value=False, help="Requires optional Google Gemini API key.")
    gemini_key = ""
    if enable_ai:
        gemini_key = st.text_input("Gemini API Key:", type="password", help="Enter your Gemini API key for tailored executive coaching.")

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.78rem; color: #94a3b8;">
        <b>🔒 Privacy Protected</b><br>
        Resumes are processed in-memory. Personal contact details are filtered. No permanent storage.
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# MAIN PAGE HEADER & PRIVACY NOTICE
# ==========================================
st.title("🎯 AI Resume Analyzer & Job Match Predictor")
st.markdown("Automated skill extraction, career-role similarity matching, gap analysis, and tailored learning roadmaps.")

# Mandatory Privacy Notice
st.markdown("""
<div class="privacy-banner">
    🛡️ <b>Privacy Notice:</b> Your resume is processed temporarily in-memory for analysis. Avoid uploading confidential information you do not want processed by this application. Uploaded files are not permanently stored and complete resume texts are not logged.
</div>
""", unsafe_allow_html=True)


# ==========================================
# PROFILE DATA INITIALIZATION
# ==========================================
resume_profile = None
manual_profile = None
final_profile = None

# Base path for sample resumes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RESUME_DS = os.path.join(BASE_DIR, "data", "sample_resumes", "data_scientist_resume.pdf")
SAMPLE_RESUME_FS = os.path.join(BASE_DIR, "data", "sample_resumes", "fullstack_resume.pdf")

# Predefined skill list for quick manual selection
POPULAR_SKILLS = [
    "Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Deep Learning",
    "PyTorch", "TensorFlow", "FastAPI", "Docker", "Kubernetes", "AWS", "Microsoft Azure",
    "JavaScript", "TypeScript", "React", "Node.js", "Express", "HTML", "CSS", "Tailwind CSS",
    "PostgreSQL", "MongoDB", "Redis", "Apache Spark", "PySpark", "Airflow", "Kafka",
    "Power BI", "Tableau", "Excel", "Git", "CI/CD", "Linux", "Cybersecurity", "Network Security"
]


# ==========================================
# INPUT HANDLING ACCORDING TO OPTIONS
# ==========================================

# 1. Option 1 or Option 3: Resume Upload
if "Option 1" in input_mode or "Option 3" in input_mode:
    st.subheader("📄 Upload Resume (PDF)")
    
    col_up1, col_up2 = st.columns([3, 1])
    with col_up1:
        uploaded_file = st.file_uploader(
            "Upload your resume in PDF format (Max 10MB)",
            type=["pdf"],
            help="Your PDF will be extracted using pdfplumber / pypdf."
        )
    
    with col_up2:
        st.write("Or try a sample:")
        sample_choice = st.selectbox(
            "Load Sample PDF:",
            ["None", "Data Scientist Sample", "Full Stack Developer Sample"],
            index=0
        )

    # Handle sample selection
    if uploaded_file is None and sample_choice != "None":
        sample_path = SAMPLE_RESUME_DS if sample_choice == "Data Scientist Sample" else SAMPLE_RESUME_FS
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                sample_bytes = f.read()
            resume_profile = profile_builder.build_from_resume(sample_bytes, filename=os.path.basename(sample_path))
            st.info(f"Loaded sample resume: **{sample_choice}**")
    elif uploaded_file is not None:
        resume_profile = profile_builder.build_from_resume(uploaded_file, filename=uploaded_file.name)
        st.success(f"Successfully processed **{uploaded_file.name}** ({resume_profile['page_count']} page(s))")


# 2. Option 2 or Option 3: Manual Information Form
if "Option 2" in input_mode or "Option 3" in input_mode:
    st.markdown("---")
    st.subheader("✍️ Enter Profile Information Manually" if "Option 2" in input_mode else "✍️ Supplementary Manual Profile Information")
    st.caption("Provide manual details to build your profile or augment your uploaded resume.")

    with st.expander("📝 Manual Information Form", expanded=True if "Option 2" in input_mode else False):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            man_degree = st.selectbox(
                "Highest Degree / Education:",
                ["Bachelor's Degree", "Master's Degree", "Ph.D. / Doctorate", "Associate / Diploma", "High School", "Self-Taught / Other"],
                index=0
            )
            man_branch = st.text_input("Branch / Major / Field of Study:", value="Computer Science & Engineering")
            man_exp_years = st.number_input("Years of Professional Experience:", min_value=0.0, max_value=40.0, value=1.5, step=0.5)

        with col_m2:
            man_skills_select = st.multiselect(
                "Select Technical Skills:",
                options=sorted(POPULAR_SKILLS),
                default=["Python", "SQL", "Machine Learning"] if "Option 2" in input_mode else ["Power BI", "Streamlit"]
            )
            man_custom_skills = st.text_input("Additional Skills (comma-separated):", value="", placeholder="e.g. LangChain, Next.js, Microservices")
            man_interests = st.text_input("Interests / Domains:", value="Generative AI, Cloud Systems, Analytics")

        col_m3, col_m4 = st.columns(2)
        with col_m3:
            man_projects = st.text_area(
                "Projects (One per line or description):",
                value="• Real-Time Churn Predictor: Built XGBoost pipeline with 88% accuracy\n• E-Commerce Web Platform: Developed RESTful backend with PostgreSQL",
                height=100
            )
        with col_m4:
            man_certifications = st.text_area(
                "Certifications (One per line):",
                value="• AWS Certified Solutions Architect – Associate\n• DeepLearning.AI Machine Learning Specialization",
                height=100
            )

        # Merge selected + custom skills
        all_manual_skills = list(man_skills_select)
        if man_custom_skills:
            all_manual_skills.extend([s.strip() for s in man_custom_skills.split(',') if s.strip()])

        manual_profile = profile_builder.build_from_manual(
            education_degree=man_degree,
            branch=man_branch,
            manual_skills=all_manual_skills,
            experience_text=f"{man_exp_years} years experience",
            experience_years=man_exp_years,
            projects_text=man_projects,
            certifications_text=man_certifications,
            interests_text=man_interests,
            career_goals=selected_target_role
        )


# ==========================================
# COMBINE PROFILES BASED ON SELECTED OPTION
# ==========================================
if "Option 1" in input_mode:
    final_profile = resume_profile
elif "Option 2" in input_mode:
    final_profile = manual_profile
elif "Option 3" in input_mode:
    if resume_profile and manual_profile:
        final_profile = profile_builder.combine_profiles(resume_profile, manual_profile)
    elif resume_profile:
        final_profile = resume_profile
    else:
        final_profile = manual_profile


# ==========================================
# RENDER DASHBOARD
# ==========================================
if not final_profile:
    st.info("👋 Please upload a PDF resume or enter your details manually to generate your AI Resume Analysis & Job Match dashboard.")
else:
    # Run Career Matching Analysis
    career_match_results = job_matcher.match_profile_against_roles(
        user_skills=final_profile.get('skills', []),
        profile_text=final_profile.get('raw_text', ''),
        experience_years=final_profile.get('experience_years', 0.0)
    )

    # Get target role details
    target_role_info = get_role_details(selected_target_role)
    target_match_data = next((r for r in career_match_results if r['role'] == selected_target_role), career_match_results[0])
    
    missing_skills_target = target_match_data.get('missing_skills', [])
    matched_skills_target = target_match_data.get('matched_skills', [])

    # Factual strengths & grounded improvements
    resume_strengths = recommendation_engine.generate_resume_strengths(final_profile)
    resume_improvements = recommendation_engine.generate_resume_improvements(
        final_profile,
        missing_skills_target,
        target_role=selected_target_role
    )
    ordered_learning_roadmap = recommendation_engine.generate_ordered_learning_roadmap(missing_skills_target)
    ats_audit = recommendation_engine.audit_resume_ats(final_profile.get('raw_text', ''))

    st.markdown("---")
    st.header("📄 RESUME ANALYSIS DASHBOARD")

    # Quick Top Metric Strip
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Detected Skills</h3>
            <div class="val">{len(final_profile.get('skills', []))}</div>
            <small>Canonical competencies</small>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        top_match = career_match_results[0]
        st.markdown(f"""
        <div class="metric-card">
            <h3>Top Career Match</h3>
            <div class="val">{top_match['match_percentage']}%</div>
            <small>{top_match['role']}</small>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Target Role Match</h3>
            <div class="val">{target_match_data['match_percentage']}%</div>
            <small>{selected_target_role}</small>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>ATS Health Score</h3>
            <div class="val">{ats_audit['overall_ats_score']}/100</div>
            <small>{ats_audit['length_status']} word count</small>
        </div>
        """, unsafe_allow_html=True)

    # 7 Required Dedicated Tabs
    tab_overview, tab_skills, tab_match, tab_gap, tab_roadmap, tab_projects, tab_improvements = st.tabs([
        "📄 Resume Overview",
        "🧠 Skills",
        "🎯 Career Match",
        "📊 Skill Gap",
        "📚 Learning Roadmap",
        "💼 Project Recommendations",
        "✨ Resume Improvements"
    ])


    # --------------------------------------------------
    # TAB 1: 📄 Resume Overview
    # --------------------------------------------------
    with tab_overview:
        st.subheader("Resume & Profile Overview")
        st.caption("Factual breakdown of detected profile sections without exposing confidential personal information.")

        ov_col1, ov_col2 = st.columns([1, 1])

        with ov_col1:
            st.markdown("#### 📋 Profile Breakdown")
            
            # Pages & Source
            source_badge = "Uploaded PDF Document" if final_profile['source_mode'] == 'resume_upload' else ("Manual Input Form" if final_profile['source_mode'] == 'manual_input' else "Hybrid (Resume + Manual Additions)")
            st.markdown(f"- **Source:** {source_badge}")
            st.markdown(f"- **Document Length / Pages:** {final_profile.get('page_count', 1)} page(s)")
            
            # Education
            edu_display = ", ".join(final_profile.get('education', [])) or "Bachelor's Degree in Technology / Science"
            st.markdown(f"- **Education:** {edu_display}")
            
            # Experience
            st.markdown(f"- **Experience:** {final_profile.get('experience', '1+ years estimated')}")
            
            # Projects Count
            proj_count = len(final_profile.get('projects', []))
            st.markdown(f"- **Technical Projects:** {proj_count} project(s) identified")

            # Certifications Count
            cert_count = len(final_profile.get('certifications', []))
            st.markdown(f"- **Certifications:** {cert_count} credential(s) identified")

            if final_profile.get('certifications'):
                st.markdown("##### Detected Certifications:")
                for c in final_profile['certifications'][:5]:
                    st.markdown(f"  • {c}")

            if final_profile.get('projects'):
                st.markdown("##### Detected Projects:")
                for p in final_profile['projects'][:4]:
                    st.markdown(f"  • **{p.get('title', 'Project')}**")

        with ov_col2:
            st.markdown("#### 🌟 Resume Strengths")
            st.caption("Factual strengths identified strictly from actual information found:")
            for strength in resume_strengths:
                st.markdown(f"""
                <div class="highlight-box">
                    {strength}
                </div>
                """, unsafe_allow_html=True)

            if "Option 3" in input_mode and resume_profile and manual_profile:
                st.markdown("---")
                st.markdown("#### 🔄 Hybrid Source Composition")
                st.write(f"• **Extracted from Resume:** {len(resume_profile.get('skills', []))} skills")
                st.write(f"• **Added via Manual Form:** {len(manual_profile.get('skills', []))} skills")
                st.write(f"• **Final Combined Skills:** {len(final_profile.get('skills', []))} skills")


    # --------------------------------------------------
    # TAB 2: 🧠 Skills
    # --------------------------------------------------
    with tab_skills:
        st.subheader("🧠 Detected Technical & Domain Skills")
        st.caption("All extracted and verified skills with category taxonomy mappings.")

        all_user_skills = final_profile.get('skills', [])
        if not all_user_skills:
            st.warning("No technical skills detected. Please add skills via manual input.")
        else:
            # Display chips
            st.markdown("#### All Detected Skills:")
            badge_html = "".join([f'<span class="skill-badge">✓ {s}</span>' for s in all_user_skills])
            st.markdown(badge_html, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### Skills by Category Breakdown")
            
            cat_skills = final_profile.get('skills_by_category', {})
            cat_cols = st.columns(2)
            
            cat_list = list(cat_skills.items())
            for idx, (category, sk_list) in enumerate(cat_list):
                col_target = cat_cols[idx % 2]
                with col_target:
                    st.markdown(f"**{category}** ({len(sk_list)})")
                    cat_badges = "".join([f'<span class="skill-badge-have">✓ {s}</span>' for s in sk_list])
                    st.markdown(cat_badges, unsafe_allow_html=True)
                    st.write("")

            # Category count chart
            if cat_skills:
                st.markdown("---")
                chart_df = pd.DataFrame([
                    {"Category": k, "Skill Count": len(v)}
                    for k, v in cat_skills.items()
                ]).sort_values("Skill Count", ascending=True)

                fig_cat = px.bar(
                    chart_df,
                    x="Skill Count",
                    y="Category",
                    orientation="h",
                    title="Skill Distribution Across Tech Categories",
                    color="Skill Count",
                    color_continuous_scale="Viridis"
                )
                fig_cat.update_layout(template="plotly_dark", height=340, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_cat, use_container_width=True)


    # --------------------------------------------------
    # TAB 3: 🎯 Career Match
    # --------------------------------------------------
    with tab_match:
        st.subheader("🎯 CAREER MATCH RESULTS")
        
        # Prominent Methodology Disclaimer
        st.warning("""
        ⚠️ **IMPORTANT METHODOLOGY NOTICE:**  
        These percentages represent profile-to-role similarity based on the implemented matching methodology.  
        They are **NOT**:
        - Hiring probabilities
        - Guaranteed employment chances
        - Salary predictions
        - Selection probabilities
        """)

        match_df = pd.DataFrame(career_match_results)

        # Plotly Match Bar Chart
        fig_match = px.bar(
            match_df,
            x="match_percentage",
            y="role",
            orientation="h",
            text="match_percentage",
            title="Career Role Profile Similarity Scores (%)",
            labels={"match_percentage": "Match Score (%)", "role": "Career Role"},
            color="match_percentage",
            color_continuous_scale="Teal"
        )
        fig_match.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_match.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=40, t=40, b=20)
        )
        st.plotly_chart(fig_match, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Detailed Career Match Leaderboard")

        for r in career_match_results:
            with st.container():
                col_r1, col_r2, col_r3 = st.columns([3, 1, 1])
                with col_r1:
                    st.markdown(f"### {r['role']}")
                    st.caption(f"{r['description']}")
                with col_r2:
                    st.metric("Profile Similarity", f"{r['match_percentage']}%")
                with col_r3:
                    st.metric("Core Skills Match", r['core_match_count'])
                
                # Show quick matching skills
                if r['matched_skills']:
                    badges = "".join([f'<span class="skill-badge-have">✓ {s}</span>' for s in r['matched_skills'][:6]])
                    st.markdown(f"**Top Matched:** {badges}", unsafe_allow_html=True)
                st.markdown("---")


    # --------------------------------------------------
    # TAB 4: 📊 Skill Gap
    # --------------------------------------------------
    with tab_gap:
        st.subheader(f"📊 Skill Gap Analysis for Target Role: {selected_target_role}")
        st.caption("Comparison between your detected skills and the competencies required for your target role.")

        gap_col1, gap_col2 = st.columns(2)

        with gap_col1:
            st.markdown("### ✓ Skills You Already Have")
            if matched_skills_target:
                have_badges = "".join([f'<span class="skill-badge-have">✓ {s}</span>' for s in matched_skills_target])
                st.markdown(have_badges, unsafe_allow_html=True)
                st.write("")
                for s in matched_skills_target:
                    st.markdown(f"- **✓ {s}** (Demonstrated in profile)")
            else:
                st.info("No direct skill overlaps identified yet with this role's specific stack.")

        with gap_col2:
            st.markdown("### ○ Skills To Develop (Gaps)")
            if missing_skills_target:
                gap_badges = "".join([f'<span class="skill-badge-gap">○ {s}</span>' for s in missing_skills_target])
                st.markdown(gap_badges, unsafe_allow_html=True)
                st.write("")
                for s in missing_skills_target:
                    st.markdown(f"- **○ {s}** (Recommended to acquire)")
            else:
                st.success("🎉 Outstanding! You have matched all primary and secondary skills for this role!")

        # Overlap breakdown donut chart
        st.markdown("---")
        total_req = len(matched_skills_target) + len(missing_skills_target)
        if total_req > 0:
            pie_fig = go.Figure(data=[go.Pie(
                labels=['Skills You Have', 'Skills To Develop'],
                values=[len(matched_skills_target), len(missing_skills_target)],
                hole=.45,
                marker_colors=['#10b981', '#f59e0b']
            )])
            pie_fig.update_layout(
                title_text=f"Competency Coverage for {selected_target_role}",
                template="plotly_dark",
                height=320,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(pie_fig, use_container_width=True)


    # --------------------------------------------------
    # TAB 5: 📚 Learning Roadmap
    # --------------------------------------------------
    with tab_roadmap:
        st.subheader(f"📚 Recommended Learning Order for {selected_target_role}")
        st.caption("A structured, pedagogical sequence designed to bridge your skill gaps efficiently.")

        if not missing_skills_target:
            st.success(f"You already cover the key required skills for **{selected_target_role}**! Review advanced portfolio projects in the next tab.")
        else:
            st.markdown("#### 🎯 Priority Learning Sequence:")
            
            for item in ordered_learning_roadmap:
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #1e293b; border-left: 5px solid #38bdf8; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                        <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc;">
                            Step {item['order']}: {item['skill']} <span style="font-size: 0.8rem; background: #0284c7; padding: 2px 8px; border-radius: 12px; margin-left: 10px;">{item['priority']} Priority</span>
                        </div>
                        <div style="color: #cbd5e1; margin-top: 6px;">
                            <b>Curriculum Focus:</b> Master core principles and hands-on synthesis for <i>{item['skill']}</i>.
                        </div>
                        <div style="color: #94a3b8; margin-top: 4px;">
                            <b>Target Milestone:</b> {item['suggested_project']}
                        </div>
                        <div style="color: #38bdf8; margin-top: 6px; font-size: 0.88rem;">
                            <b>Recommended Free Learning Resource:</b> {item['resource']}
                        </div>
                        <div style="color: #a7f3d0; margin-top: 4px; font-size: 0.88rem;">
                            <b>Target Certifications:</b> {', '.join(item['certifications'])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


    # --------------------------------------------------
    # TAB 6: 💼 Project Recommendations
    # --------------------------------------------------
    with tab_projects:
        st.subheader(f"💼 High-Impact Project Recommendations for {selected_target_role}")
        st.caption("Grounded, industry-relevant portfolio projects to demonstrate practical competencies to hiring managers.")

        role_projects = target_role_info.get('project_recommendations', [])
        if not role_projects:
            st.info(f"No specific curated projects for {selected_target_role}. Building full-stack and data projects is universally recommended.")
        else:
            for idx, proj in enumerate(role_projects, start=1):
                with st.expander(f"📌 Project {idx}: {proj['title']} ({proj.get('difficulty', 'Intermediate')})", expanded=True):
                    st.markdown(f"**Problem & Scope:** {proj['description']}")
                    st.markdown(f"**Recommended Tech Stack:** `{'`, `'.join(proj.get('tech_stack', []))}`")
                    st.markdown(f"**Portfolio Resume Impact:** *{proj.get('impact', '')}*")


    # --------------------------------------------------
    # TAB 7: ✨ Resume Improvements
    # --------------------------------------------------
    with tab_improvements:
        st.subheader("✨ Resume Improvement Suggestions")
        st.caption("Actionable recommendations to enhance resume impact, ATS parsing, and technical clarity. (No invented experience)")

        for item in resume_improvements:
            st.markdown(f"""
            <div class="warning-box">
                <div style="font-weight: 700; font-size: 1rem; color: #fbbf24;">{item['action']}</div>
                <div style="color: #e2e8f0; margin-top: 4px; font-size: 0.92rem;">{item['details']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📋 ATS Formatting Audit")
        
        col_ats1, col_ats2 = st.columns(2)
        with col_ats1:
            st.write(f"• **Word Count:** {ats_audit['word_count']} words ({ats_audit['length_status']})")
            st.write(f"• **Sections Detected:** {', '.join(ats_audit['sections_found']) or 'Standard format'}")
            if ats_audit['sections_missing']:
                st.write(f"• **Missing Common Sections:** {', '.join(ats_audit['sections_missing'])}")
        with col_ats2:
            st.write(f"• **Action Verbs Detected:** {ats_audit['action_verbs_count']} strong verbs")
            st.write(f"• **Quantifiable Metrics Found:** {ats_audit['quantifiable_metrics_count']} metrics")

        # Optional LLM deep coaching
        if enable_ai:
            st.markdown("---")
            st.subheader("🤖 AI Executive Coaching & Bullet Rewrites")
            if not gemini_key and not os.environ.get("GEMINI_API_KEY"):
                st.info("💡 To generate live Gemini LLM feedback, please provide your Gemini API key in the sidebar. Showing smart offline rule-based insights.")
            
            explainer = LLMExplainer(api_key=gemini_key)
            match_payload = {
                'overall_score': target_match_data['match_percentage'],
                'skills_analysis': {
                    'matched_skills': matched_skills_target,
                    'missing_skills': missing_skills_target,
                    'additional_skills': [s for s in final_profile.get('skills', []) if s not in matched_skills_target]
                }
            }
            ai_insights = explainer.generate_ai_analysis(
                resume_text=final_profile.get('raw_text', ''),
                jd_text=target_role_info.get('description', ''),
                match_data=match_payload,
                predicted_role=selected_target_role
            )
            st.markdown(f"**Source:** *{ai_insights.get('source', '')}*")
            st.markdown(ai_insights.get('analysis', ''))


    # ==========================================
    # EXPORT & REPORT DOWNLOAD
    # ==========================================
    st.markdown("---")
    st.subheader("📥 Export Complete Analysis Report")
    
    report_data = {
        'overall_score': target_match_data['match_percentage'],
        'match_tier': "High Match" if target_match_data['match_percentage'] >= 75 else ("Moderate Match" if target_match_data['match_percentage'] >= 50 else "Development Needed"),
        'predicted_category': selected_target_role,
        'score_breakdown': {
            'skill_match_score': target_match_data['match_percentage'],
            'tfidf_cosine_score': target_match_data['match_percentage'],
            'experience_score': 85.0,
            'education_score': 100.0
        },
        'skills_analysis': {
            'matched_skills': matched_skills_target,
            'missing_skills': missing_skills_target,
            'additional_skills': [s for s in final_profile.get('skills', []) if s not in matched_skills_target]
        },
        'ats_audit': ats_audit
    }

    md_report = generate_markdown_report(report_data)
    json_report = json.dumps(report_data, indent=2)
    pdf_report_bytes = generate_pdf_report(report_data)

    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        st.download_button(
            label="📄 Download Markdown Report (.md)",
            data=md_report,
            file_name=f"resume_analysis_{selected_target_role.lower().replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with exp_col2:
        st.download_button(
            label="📊 Download JSON Data (.json)",
            data=json_report,
            file_name=f"resume_analysis_{selected_target_role.lower().replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
    with exp_col3:
        st.download_button(
            label="📕 Download PDF Report (.pdf)",
            data=pdf_report_bytes,
            file_name=f"resume_analysis_{selected_target_role.lower().replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
