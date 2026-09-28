"""
Text Cleaner and Preprocessor Module
Provides NLP preprocessing, tokenization, text normalization, and section segmentation.
"""

import re
import unicodedata
from typing import List, Dict, Set

# Comprehensive built-in stopwords list to ensure 100% offline standalone capability
STOPWORDS: Set[str] = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'cannot', 'could',
    'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each', 'few', 'for',
    'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll',
    'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i', 'i\'d',
    'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s', 'me',
    'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other',
    'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll', 'she\'s',
    'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs', 'them',
    'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'this',
    'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll',
    'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which',
    'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d',
    'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves',
    # Common resume boilerplate noise words
    'etc', 'e.g', 'eg', 'ie', 'i.e', 'also', 'using', 'used', 'worked', 'working', 'responsible', 'including',
    'within', 'well', 'across', 'various', 'help', 'helped', 'helping'
}

# Strong action verbs for resume audit
ACTION_VERBS: Set[str] = {
    'accelerated', 'achieved', 'administered', 'analyzed', 'architected', 'automated', 'built', 'calculated',
    'championed', 'collaborated', 'composed', 'conceived', 'configured', 'constructed', 'converted', 'coordinated',
    'created', 'customized', 'debugged', 'decreased', 'delivered', 'deployed', 'designed', 'developed', 'devised',
    'directed', 'discovered', 'documented', 'doubled', 'drafted', 'engineered', 'enhanced', 'established',
    'evaluated', 'executed', 'expanded', 'expedited', 'formulated', 'generated', 'guided', 'headed', 'implemented',
    'improved', 'increased', 'initiated', 'inspected', 'installed', 'instituted', 'integrated', 'introduced',
    'invented', 'investigated', 'launched', 'led', 'maintained', 'managed', 'maximized', 'mentored', 'minimized',
    'modernized', 'monitored', 'negotiated', 'optimized', 'orchestrated', 'organized', 'overhauled', 'oversaw',
    'performed', 'pioneered', 'planned', 'programmed', 'published', 'reduced', 'refactored', 'reorganized',
    'resolved', 'restructured', 'revamped', 'scaled', 'scheduled', 'secured', 'simplified', 'spearheaded',
    'standardized', 'streamlined', 'strengthened', 'supervised', 'surpassed', 'trained', 'transformed',
    'troubleshot', 'upgraded', 'validated', 'yielded'
}


def normalize_text(text: str) -> str:
    """
    Normalizes unicode characters, standardizes linebreaks and spaces.
    """
    if not text or not isinstance(text, str):
        return ""
    # Normalize unicode (e.g., curly quotes, non-breaking spaces)
    text = unicodedata.normalize('NFKD', text)
    # Replace weird hyphens/dashes with standard '-'
    text = re.sub(r'[\u2010-\u2015\u2212]', '-', text)
    # Replace weird quotes
    text = re.sub(r'[\u2018\u2019\u201A\u201B]', "'", text)
    text = re.sub(r'[\u201C\u201D\u201E\u201F]', '"', text)
    # Replace bullet characters with newline or space
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB\u25CF\u25CB\u25A0\u25A1]', '\n- ', text)
    # Standardize whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def clean_for_nlp(text: str, remove_stopwords: bool = True, preserve_skills_syntax: bool = True) -> str:
    """
    Cleans text for TF-IDF / Bag of Words processing while preserving technical tokens like C++, C#, .NET.
    """
    if not text:
        return ""

    text = normalize_text(text).lower()

    # If preserving skill syntax, temporarily replace key tokens
    if preserve_skills_syntax:
        replacements = {
            'c++': ' cpptoken ',
            'c#': ' csharptoken ',
            '.net': ' dotnettoken ',
            'node.js': ' nodejstoken ',
            'react.js': ' reactjstoken ',
            'vue.js': ' vuejstoken ',
            'ci/cd': ' cicdtoken ',
            'tcp/ip': ' tcpiptoken '
        }
        for k, v in replacements.items():
            text = text.replace(k, v)

    # Remove URLs and Emails
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', ' ', text)

    # Remove punctuation except alphanumeric and space
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    # Restore tokens
    if preserve_skills_syntax:
        rev_replacements = {
            'cpptoken': 'c++',
            'csharptoken': 'c#',
            'dotnettoken': 'dotnet',
            'nodejstoken': 'nodejs',
            'reactjstoken': 'reactjs',
            'vuejstoken': 'vuejs',
            'cicdtoken': 'cicd',
            'tcpiptoken': 'tcpip'
        }
        for k, v in rev_replacements.items():
            text = text.replace(k, v)

    tokens = text.split()

    if remove_stopwords:
        tokens = [w for w in tokens if w not in STOPWORDS and len(w) > 1]

    return " ".join(tokens)


def tokenize_sentences(text: str) -> List[str]:
    """
    Splits text into sentences using regex boundary detection.
    """
    text = normalize_text(text)
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])|\n+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 5]


def extract_sections(text: str) -> Dict[str, str]:
    """
    Segments resume into standard sections:
    - Summary / Objective
    - Experience / Work History
    - Education
    - Skills
    - Projects
    - Certifications / Awards
    """
    normalized = normalize_text(text)
    
    section_patterns = {
        'summary': r'(?:summary|professional summary|executive summary|profile|about me|objective|career objective)',
        'experience': r'(?:work experience|professional experience|employment history|experience|work history)',
        'education': r'(?:education|academic background|academics|qualifications|educational qualifications)',
        'skills': r'(?:skills|technical skills|key skills|core competencies|areas of expertise|technologies|tools & technologies)',
        'projects': r'(?:projects|personal projects|academic projects|key projects)',
        'certifications': r'(?:certifications|certificates|licenses|achievements|awards|publications)'
    }

    # Match section headers at line beginnings
    all_headers = "|".join(f"(?P<{k}>{v})" for k, v in section_patterns.items())
    header_regex = re.compile(rf'(?im)^[\s#*_-]*({all_headers})[\s:*_-]*$')

    splits = list(header_regex.finditer(normalized))
    
    sections: Dict[str, str] = {
        'summary': '',
        'experience': '',
        'education': '',
        'skills': '',
        'projects': '',
        'certifications': '',
        'other': ''
    }

    if not splits:
        sections['other'] = normalized
        return sections

    # Content before first header
    if splits[0].start() > 0:
        sections['summary'] = normalized[:splits[0].start()].strip()

    for idx, match in enumerate(splits):
        matched_category = None
        for cat, pattern in section_patterns.items():
            if match.group(cat):
                matched_category = cat
                break
        
        if not matched_category:
            matched_category = 'other'

        start_pos = match.end()
        end_pos = splits[idx + 1].start() if idx + 1 < len(splits) else len(normalized)
        section_content = normalized[start_pos:end_pos].strip()

        if sections.get(matched_category):
            sections[matched_category] += "\n" + section_content
        else:
            sections[matched_category] = section_content

    return sections
