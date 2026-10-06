"""
MediScan AI - Document Classifier
Demonstrates: functions, strings, loops, branching, lists, sets, dictionaries
Classifies medical documents into categories using rule-based text analysis.
"""
import re
from typing import Tuple


# Keyword sets for each document category
# Demonstrates: sets for fast membership testing
BLOOD_REPORT_KEYWORDS = {
    'hemoglobin', 'hematocrit', 'rbc', 'wbc', 'platelets', 'mcv', 'mchc',
    'lymphocytes', 'neutrophils', 'eosinophils', 'basophils', 'monocytes',
    'differential count', 'complete blood', 'cbc', 'blood count', 'erythrocyte',
    'leukocyte', 'thrombocyte', 'hgb', 'plt', 'haemoglobin',
}

LAB_REPORT_KEYWORDS = {
    'glucose', 'creatinine', 'urea', 'bun', 'sodium', 'potassium', 'chloride',
    'calcium', 'albumin', 'total protein', 'bilirubin', 'alt', 'ast', 'alkaline phosphatase',
    'cholesterol', 'triglycerides', 'hdl', 'ldl', 'thyroid', 'tsh', 'uric acid',
    'ferritin', 'vitamin', 'hba1c', 'insulin', 'cortisol', 'testosterone', 'prolactin',
    'laboratory', 'biochemistry', 'pathology', 'specimen', 'serum', 'plasma',
}

PRESCRIPTION_KEYWORDS = {
    'prescribed', 'rx', 'tablet', 'capsule', 'mg', 'dosage', 'dose',
    'twice daily', 'once daily', 'thrice', 'medication', 'drug', 'pharmacy',
    'refill', 'prescription', 'doctor', 'physician', 'patient name', 'sig:',
    'take', 'apply', 'inject', 'inhale', 'syrup', 'injection',
}

MEDICAL_RECORD_KEYWORDS = {
    'diagnosis', 'clinical notes', 'admission', 'discharge', 'history',
    'complaint', 'examination', 'treatment', 'surgery', 'operation',
    'prognosis', 'follow up', 'referral', 'medical history', 'chief complaint',
    'physical examination', 'assessment', 'plan', 'icd', 'soap',
}

RADIOLOGY_KEYWORDS = {
    'x-ray', 'xray', 'mri', 'ct scan', 'ultrasound', 'sonography',
    'radiograph', 'impression', 'findings', 'echo', 'echocardiogram',
    'mammogram', 'pet scan', 'bone scan', 'radiology', 'imaging',
}

# Category metadata - demonstrates: dictionary of dictionaries
CATEGORY_INFO = {
    'Blood Report': {
        'keywords': BLOOD_REPORT_KEYWORDS,
        'icon': '🩸',
        'description': 'Complete Blood Count or related blood analysis',
        'color': 'danger',
    },
    'Laboratory Report': {
        'keywords': LAB_REPORT_KEYWORDS,
        'icon': '🔬',
        'description': 'Biochemistry, hormone, or metabolic panel results',
        'color': 'primary',
    },
    'Prescription': {
        'keywords': PRESCRIPTION_KEYWORDS,
        'icon': '💊',
        'description': 'Medical prescription from a healthcare provider',
        'color': 'success',
    },
    'Medical Record': {
        'keywords': MEDICAL_RECORD_KEYWORDS,
        'icon': '📋',
        'description': 'Clinical notes, discharge summary, or patient history',
        'color': 'info',
    },
    'Radiology Report': {
        'keywords': RADIOLOGY_KEYWORDS,
        'icon': '🩻',
        'description': 'Imaging report (X-ray, MRI, CT scan, ultrasound)',
        'color': 'secondary',
    },
}


def classify_document(extracted_text: str) -> Tuple[str, float, str]:
    """
    Classify a medical document based on keyword analysis.

    Demonstrates: functions, loops, branching, strings, dictionaries, lists

    Args:
        extracted_text: The text content of the document

    Returns:
        Tuple of (category, confidence_score, icon)
    """
    if not extracted_text or not extracted_text.strip():
        return 'General Medical Document', 0.0, '📄'

    # Normalize text for matching
    text_lower = extracted_text.lower()

    # Count keyword matches for each category
    # Demonstrates: dictionary comprehension, loops, string operations
    scores = {}
    for category, info in CATEGORY_INFO.items():
        keyword_set = info['keywords']
        match_count = 0

        for keyword in keyword_set:
            # Count occurrences of each keyword
            if keyword in text_lower:
                match_count += 1

        scores[category] = match_count

    # Find best matching category
    if not any(scores.values()):
        return 'General Medical Document', 0.0, '📄'

    best_category = max(scores, key=lambda k: scores[k])
    best_score = scores[best_category]

    # Calculate confidence (0.0 to 1.0)
    total_keywords = len(CATEGORY_INFO[best_category]['keywords'])
    confidence = min(best_score / max(total_keywords * 0.2, 1), 1.0)

    icon = CATEGORY_INFO[best_category]['icon']

    # If scores are too close, return combined label
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_scores) >= 2 and sorted_scores[1][1] >= sorted_scores[0][1] * 0.8:
        # Second category is close - combine
        combined = f"{sorted_scores[0][0]} / {sorted_scores[1][0]}"
        return combined, confidence, icon

    return best_category, confidence, icon


def get_document_keywords_found(text: str, category: str) -> list:
    """
    Return list of matched keywords for a given category.
    Demonstrates: list comprehension, string methods, sets
    """
    if category not in CATEGORY_INFO:
        return []

    text_lower = text.lower()
    keywords = CATEGORY_INFO[category]['keywords']

    # List comprehension - demonstrates list operations
    matched = [kw for kw in keywords if kw in text_lower]
    return sorted(matched)


def get_all_category_scores(text: str) -> dict:
    """
    Get match scores for all categories.
    Demonstrates: dictionary operations, loops
    """
    text_lower = text.lower()
    scores = {}

    for category, info in CATEGORY_INFO.items():
        score = sum(1 for kw in info['keywords'] if kw in text_lower)
        scores[category] = {
            'score': score,
            'icon': info['icon'],
            'description': info['description'],
        }

    return scores


def extract_patient_info(text: str) -> dict:
    """
    Extract basic patient information using regex patterns.
    Demonstrates: regular expressions, dictionaries, string processing
    """
    info = {
        'patient_name': '',
        'patient_age': '',
        'patient_gender': '',
        'report_date': '',
        'lab_name': '',
        'doctor_name': '',
    }

    # Name patterns
    name_patterns = [
        r'(?:patient\s*name|name)\s*[:.]?\s*([A-Z][a-zA-Z\s]+?)(?:\n|$|,)',
        r'(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+([A-Z][a-zA-Z\s]+?)(?:\n|$|,)',
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['patient_name'] = match.group(1).strip()
            break

    # Age patterns
    age_patterns = [
        r'(?:age|age/sex)\s*[:.]?\s*(\d{1,3})\s*(?:years?|yrs?|Y)',
        r'\b(\d{1,3})\s*(?:years?\s*old|yr\s*old)',
        r'age\s*:\s*(\d{1,3})',
    ]
    for pattern in age_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['patient_age'] = match.group(1).strip()
            break

    # Gender patterns
    gender_match = re.search(
        r'(?:sex|gender)\s*[:.]?\s*(male|female|m|f)\b',
        text, re.IGNORECASE
    )
    if gender_match:
        g = gender_match.group(1).strip().upper()
        info['patient_gender'] = 'Male' if g in ('M', 'MALE') else 'Female'

    # Date patterns
    date_patterns = [
        r'(?:date|report\s*date|collection\s*date)\s*[:.]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['report_date'] = match.group(1).strip()
            break

    # Doctor name
    doctor_match = re.search(
        r'(?:dr\.|doctor|physician|referred\s*by)\s*[:.]?\s*([A-Z][a-zA-Z\s.]+?)(?:\n|$|,)',
        text, re.IGNORECASE
    )
    if doctor_match:
        info['doctor_name'] = doctor_match.group(1).strip()

    return info
