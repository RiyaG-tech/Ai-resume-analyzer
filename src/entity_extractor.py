"""
Entity and Information Extraction Module
Extracts Candidate Education, Branch, Experience, Projects, Certifications,
Technologies/Tools, Links, and Quantifiable metrics while supporting privacy masking.
"""

import re
from typing import Dict, List, Any, Optional
from src.text_cleaner import ACTION_VERBS, normalize_text, extract_sections


def extract_emails(text: str) -> List[str]:
    """Extracts valid email addresses from text."""
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    matches = re.findall(email_pattern, text)
    return list(dict.fromkeys(matches))


def extract_phone_numbers(text: str) -> List[str]:
    """Extracts phone numbers in various international and domestic formats."""
    phone_pattern = r'(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}|\b\d{10}\b|\+\d{1,3}\s\d{10})'
    candidates = re.findall(phone_pattern, text)
    cleaned_phones = []
    for c in candidates:
        digits = re.sub(r'\D', '', c)
        if 10 <= len(digits) <= 15:
            cleaned_phones.append(c.strip())
    return list(dict.fromkeys(cleaned_phones))


def extract_links(text: str) -> Dict[str, List[str]]:
    """Extracts LinkedIn, GitHub, Portfolio, and other external links."""
    links = {
        'linkedin': [],
        'github': [],
        'portfolio_other': []
    }
    
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+|linkedin\.com/in/[^\s<>"]+|github\.com/[^\s<>"]+'
    matches = re.findall(url_pattern, text, re.IGNORECASE)
    
    for url in matches:
        u_lower = url.lower()
        if 'linkedin.com' in u_lower:
            links['linkedin'].append(url)
        elif 'github.com' in u_lower:
            links['github'].append(url)
        else:
            links['portfolio_other'].append(url)

    for k in links:
        links[k] = list(dict.fromkeys(links[k]))
        
    return links


def extract_education_details(text: str) -> List[Dict[str, str]]:
    """
    Extracts degrees, majors/branches, and institutions.
    """
    sections = extract_sections(text)
    edu_text = sections.get('education', '')
    if not edu_text or len(edu_text.strip()) < 10:
        edu_text = text  # fallback to search full text

    degree_patterns = [
        (r'\b(ph\.?d\.?|doctor of philosophy|doctorate)\b', 'Ph.D. / Doctorate'),
        (r'\b(master of science|m\.?s\.?|m\.?tech\.?|master of technology|m\.?c\.?a\.?|mba|master of business administration|m\.?e\.?)\b', "Master's Degree"),
        (r'\b(bachelor of technology|b\.?tech\.?|b\.?s\.?|bachelor of science|b\.?e\.?|bachelor of engineering|b\.?c\.?a\.?|b\.?a\.?|bachelor of arts|b\.?com\.?|bba)\b', "Bachelor's Degree"),
        (r'\b(associate degree|diploma in \w+)\b', 'Associate / Diploma'),
        (r'\b(high school|secondary education|12th grade|cbse|icse)\b', 'High School')
    ]
    
    branch_patterns = [
        (r'\b(computer science|computer science & engineering|cse|information technology|it|software engineering)\b', 'Computer Science / IT'),
        (r'\b(data science|artificial intelligence|ai & ds|machine learning)\b', 'Data Science & AI'),
        (r'\b(electronics & communication|ece|electrical engineering|eee)\b', 'Electrical / Electronics'),
        (r'\b(mechanical engineering|mech|civil engineering)\b', 'Mechanical / Civil'),
        (r'\b(business administration|finance|marketing|management)\b', 'Business & Management'),
        (r'\b(mathematics|statistics|physics)\b', 'Mathematics / Statistics')
    ]
    
    found_degrees = []
    normalized = edu_text.lower()
    
    for pattern, degree_level in degree_patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            found_degrees.append(degree_level)

    found_degrees = list(dict.fromkeys(found_degrees))

    found_branches = []
    for pattern, branch_name in branch_patterns:
        if re.search(pattern, normalized, re.IGNORECASE):
            found_branches.append(branch_name)

    found_branches = list(dict.fromkeys(found_branches))

    result = []
    if found_degrees:
        for deg in found_degrees:
            result.append({
                'degree': deg,
                'branch': found_branches[0] if found_branches else 'Engineering / General Science'
            })
    elif found_branches:
        result.append({
            'degree': "Bachelor's Degree (Estimated)",
            'branch': found_branches[0]
        })

    return result


def extract_education(text: str) -> List[str]:
    """Simple degree list extractor for backward compatibility."""
    details = extract_education_details(text)
    if details:
        return [f"{d['degree']} ({d['branch']})" if d.get('branch') else d['degree'] for d in details]
    return []


def extract_years_of_experience(text: str) -> Dict[str, Any]:
    """
    Estimates total years of experience stated in text or calculated via date ranges.
    """
    explicit_pattern = r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|work|industry|software|professional)'
    matches = re.findall(explicit_pattern, text, re.IGNORECASE)
    
    explicit_years = [float(m) for m in matches if float(m) < 40]
    max_explicit = max(explicit_years) if explicit_years else 0.0

    year_range_pattern = r'\b(20\d{2}|19\d{2})\s*(?:-|–|—|to)\s*(20\d{2}|present|current|now)\b'
    range_matches = re.findall(year_range_pattern, text, re.IGNORECASE)
    
    calculated_years = 0.0
    current_year = 2026
    for start, end in range_matches:
        try:
            start_yr = int(start)
            if end.lower() in ['present', 'current', 'now']:
                end_yr = current_year
            else:
                end_yr = int(end)
            diff = end_yr - start_yr
            if 0 <= diff <= 40:
                calculated_years += diff
        except Exception:
            continue

    total_est = max(max_explicit, min(calculated_years, 35.0))

    return {
        'estimated_years': round(total_est, 1),
        'explicit_mentions': explicit_years,
        'date_ranges_found': len(range_matches)
    }


def extract_projects_list(text: str) -> List[Dict[str, str]]:
    """
    Extracts structured project entries from resume text or Projects section.
    """
    sections = extract_sections(text)
    proj_text = sections.get('projects', '')
    if not proj_text or len(proj_text.strip()) < 15:
        # Check general text for project headers
        proj_pattern = r'(?:Project\s*\d*[:\-]|Title[:\-]|\n[•\*\-]\s*)([^\n]+)'
        lines = [line.strip() for line in text.split('\n') if any(w in line.lower() for w in ['project', 'built', 'developed', 'created', 'system', 'app', 'model', 'dashboard'])]
        clean_lines = [l for l in lines if 15 < len(l) < 120 and not l.lower().startswith('skills')]
        return [{'title': l.lstrip('-*• ')} for l in clean_lines[:5]]

    # Parse bullet items in projects section
    project_entries = []
    blocks = re.split(r'\n\s*\n|\n(?=[A-Z0-9][\w\s\-]{3,40}:)|\n(?=[•\*\-]\s+[A-Z])', proj_text)
    for b in blocks:
        clean_b = b.strip()
        if len(clean_b) > 15:
            first_line = clean_b.split('\n')[0].strip().lstrip('-*• ')
            project_entries.append({
                'title': first_line[:80],
                'details': clean_b
            })

    return project_entries[:6]


def extract_certifications_list(text: str) -> List[str]:
    """
    Extracts recognized certifications and licenses from text.
    """
    sections = extract_sections(text)
    cert_text = sections.get('certifications', '')
    search_space = cert_text if (cert_text and len(cert_text.strip()) > 10) else text

    known_cert_keywords = [
        "AWS Certified", "Azure Fundamentals", "Azure Solutions Architect", "GCP Professional",
        "Google Cloud Associate", "CKA", "CKAD", "Docker Certified", "CompTIA", "CISSP", "CEH",
        "TensorFlow Developer", "DeepLearning.AI", "Meta Front-End", "Meta Back-End",
        "Oracle Certified", "PSM I", "CSM", "Power BI Data Analyst", "Tableau Certified",
        "PCEP", "PCAP", "PMP", "HashiCorp Certified", "Coursera", "Udemy", "edX"
    ]

    certs_found = []
    for cert in known_cert_keywords:
        if re.search(rf'\b{re.escape(cert)}\b', search_space, re.IGNORECASE):
            certs_found.append(cert)

    # Also parse bullet points in certifications section
    if cert_text:
        for line in cert_text.split('\n'):
            line_s = line.strip().lstrip('-*• ')
            if 10 < len(line_s) < 90 and not any(line_s.lower() == c.lower() for c in certs_found):
                certs_found.append(line_s)

    return list(dict.fromkeys(certs_found))[:8]


def extract_quantifiable_metrics(text: str) -> List[str]:
    """
    Identifies impact statements with percentages, dollar amounts, or multipliers.
    """
    metric_pattern = r'([^.\n]*?(?:\d+%\s*|\$\s*\d+[\d,]*|\b\d+x\b|\b\d+\s*(?:k|m|million|billion)\b|\bincreased\b|\breduced\b|\boptimized\b)[^.\n]*)'
    matches = re.findall(metric_pattern, text, re.IGNORECASE)
    
    clean_metrics = []
    for m in matches:
        m_str = m.strip()
        if 15 < len(m_str) < 180 and any(c.isdigit() for c in m_str):
            clean_metrics.append(m_str)
            
    return clean_metrics[:8]


def extract_action_verbs_used(text: str) -> Dict[str, Any]:
    """
    Finds action verbs used in resume bullets to measure writing strength.
    """
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    found_verbs = [w for w in words if w in ACTION_VERBS]
    unique_verbs = list(dict.fromkeys(found_verbs))
    
    return {
        'unique_action_verbs': unique_verbs,
        'count': len(unique_verbs),
        'score': min(100, int((len(unique_verbs) / 12) * 100))
    }


def extract_all_entities(text: str) -> Dict[str, Any]:
    """
    Aggregates all entity information into a comprehensive structured dictionary.
    """
    return {
        'emails': extract_emails(text),
        'phone_numbers': extract_phone_numbers(text),
        'links': extract_links(text),
        'education_details': extract_education_details(text),
        'education': extract_education(text),
        'experience_metrics': extract_years_of_experience(text),
        'projects': extract_projects_list(text),
        'certifications': extract_certifications_list(text),
        'quantifiable_achievements': extract_quantifiable_metrics(text),
        'action_verbs': extract_action_verbs_used(text)
    }
