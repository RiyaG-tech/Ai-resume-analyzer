"""
PDF and Document Text Extraction Module
Supports pdfplumber, pypdf fallback, and text/docx parsing with metadata extraction.
"""

import io
from typing import Dict, Any, Optional
import pypdf
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


def extract_text_from_pdf(file_bytes_or_path: Any) -> Dict[str, Any]:
    """
    Extracts text and metadata from a PDF file using pdfplumber with fallback to pypdf.
    Returns:
        {
            'text': str,
            'page_count': int,
            'extractor_used': str,
            'metadata': dict,
            'status': 'success' | 'error',
            'error_message': str | None
        }
    """
    result = {
        'text': '',
        'page_count': 0,
        'extractor_used': 'none',
        'metadata': {},
        'status': 'success',
        'error_message': None
    }

    # Convert to bytes buffer if needed
    if isinstance(file_bytes_or_path, (str, bytes)):
        if isinstance(file_bytes_or_path, str):
            with open(file_bytes_or_path, 'rb') as f:
                stream = io.BytesIO(f.read())
        else:
            stream = io.BytesIO(file_bytes_or_path)
    elif hasattr(file_bytes_or_path, 'read'):
        # UploadedFile from Streamlit or BytesIO
        content = file_bytes_or_path.read()
        if hasattr(file_bytes_or_path, 'seek'):
            file_bytes_or_path.seek(0)
        stream = io.BytesIO(content)
    else:
        result['status'] = 'error'
        result['error_message'] = 'Unsupported file input type.'
        return result

    # 1. Try pdfplumber
    if HAS_PDFPLUMBER:
        try:
            stream.seek(0)
            with pdfplumber.open(stream) as pdf:
                result['page_count'] = len(pdf.pages)
                result['metadata'] = pdf.metadata or {}
                extracted_pages = []
                for page in pdf.pages:
                    page_text = page.extract_text(layout=True)
                    if not page_text:
                        # Try without layout parameter
                        page_text = page.extract_text()
                    if page_text:
                        extracted_pages.append(page_text)
                
                full_text = "\n\n".join(extracted_pages).strip()
                if full_text:
                    result['text'] = full_text
                    result['extractor_used'] = 'pdfplumber'
                    return result
        except Exception as e:
            # Fallback to pypdf
            pass

    # 2. Fallback to pypdf
    try:
        stream.seek(0)
        reader = pypdf.PdfReader(stream)
        result['page_count'] = len(reader.pages)
        if reader.metadata:
            result['metadata'] = {k: str(v) for k, v in reader.metadata.items()}
        
        extracted_pages = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                extracted_pages.append(t)
        
        full_text = "\n\n".join(extracted_pages).strip()
        result['text'] = full_text
        result['extractor_used'] = 'pypdf'
        
        if not full_text:
            result['status'] = 'warning'
            result['error_message'] = 'PDF parsed successfully but yielded empty text. It may be a scanned image-based PDF.'
        return result
    except Exception as e:
        result['status'] = 'error'
        result['error_message'] = f'Failed to extract text from PDF: {str(e)}'
        return result


def extract_text_from_docx(file_bytes_or_path: Any) -> Dict[str, Any]:
    """
    Extracts text from a DOCX document.
    """
    result = {
        'text': '',
        'page_count': 1,
        'extractor_used': 'python-docx',
        'metadata': {},
        'status': 'success',
        'error_message': None
    }

    if not HAS_DOCX:
        result['status'] = 'error'
        result['error_message'] = 'python-docx library is not installed.'
        return result

    try:
        if isinstance(file_bytes_or_path, str):
            doc = docx.Document(file_bytes_or_path)
        elif hasattr(file_bytes_or_path, 'read'):
            content = file_bytes_or_path.read()
            if hasattr(file_bytes_or_path, 'seek'):
                file_bytes_or_path.seek(0)
            doc = docx.Document(io.BytesIO(content))
        else:
            doc = docx.Document(io.BytesIO(file_bytes_or_path))

        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())
        
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))

        result['text'] = "\n\n".join(full_text)
        return result
    except Exception as e:
        result['status'] = 'error'
        result['error_message'] = f'Failed to extract text from DOCX: {str(e)}'
        return result


def extract_document(file_obj: Any, filename: str) -> Dict[str, Any]:
    """
    Generic dispatcher based on file extension.
    """
    fname = filename.lower()
    if fname.endswith('.pdf'):
        return extract_text_from_pdf(file_obj)
    elif fname.endswith('.docx') or fname.endswith('.doc'):
        return extract_text_from_docx(file_obj)
    elif fname.endswith('.txt'):
        try:
            if hasattr(file_obj, 'read'):
                raw = file_obj.read()
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
            else:
                raw = file_obj
            
            if isinstance(raw, bytes):
                text = raw.decode('utf-8', errors='ignore')
            else:
                text = str(raw)
            
            return {
                'text': text,
                'page_count': 1,
                'extractor_used': 'raw_text',
                'metadata': {},
                'status': 'success',
                'error_message': None
            }
        except Exception as e:
            return {
                'text': '',
                'page_count': 0,
                'extractor_used': 'raw_text',
                'metadata': {},
                'status': 'error',
                'error_message': str(e)
            }
    else:
        return {
            'text': '',
            'page_count': 0,
            'extractor_used': 'none',
            'metadata': {},
            'status': 'error',
            'error_message': f'Unsupported file format: {filename}'
        }
