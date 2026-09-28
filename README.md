# 🎯 AI Resume Analyzer & Job Match Predictor

An enterprise-grade, privacy-conscious Streamlit application that extracts technical competencies from PDF resumes and manual forms, matches candidate profiles against industry career taxonomies, performs skill gap analysis, and constructs structured pedagogical learning roadmaps.

---

## 🚀 Key Features

### 1. Flexible Multi-Source Profile Building
- **Option 1: Upload Resume (PDF)** — High-precision PDF text extraction using `pdfplumber` with fallback to `pypdf`.
- **Option 2: Enter Information Manually** — Fully functional without an uploaded resume. Accepts Degree, Branch, Skills, Experience, Projects, Certifications, and Interests.
- **Option 3: Hybrid Blend (Resume + Manual Input)** — Combines extracted resume information with manual entries seamlessly.

### 2. 7-Tab Resume Analysis Dashboard
- 📄 **Resume Overview:** Non-invasive summary of detected pages, education, experience, projects, certifications, and factual strengths.
- 🧠 **Skills:** Canonical skill tags with categorized breakdown and interactive distribution visualization.
- 🎯 **Career Match:** Ranked career-role similarity percentages with mandatory methodology disclaimers.
- 📊 **Skill Gap:** Side-by-side comparison of *Skills You Already Have* vs *Skills To Develop*.
- 📚 **Learning Roadmap:** Ordered pedagogical sequence with curriculum focus, milestone projects, and curated learning resources.
- 💼 **Project Recommendations:** Role-specific, portfolio-worthy project blueprints with tech stacks and impact statements.
- ✨ **Resume Improvements:** Factual, non-inventive advice and ATS formatting audits (plus optional Google Gemini AI deep review).

### 3. Strict Privacy Architecture
- Resumes are processed **in-memory** and not saved permanently.
- No logging of full resume content.
- Personal identifiable contact details (phone numbers, addresses, emails) are filtered from public displays.
- External LLM API calls are only made if explicitly enabled by the user.

---

## 💻 How to Run the Application

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the Streamlit application
streamlit run app.py
```
