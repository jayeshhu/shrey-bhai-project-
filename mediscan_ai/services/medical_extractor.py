"""
MediScan AI - Medical Data Extractor
Demonstrates: Regular Expressions, lists, tuples, dictionaries, functions, loops, string processing
Extracts structured medical test data from raw text using regex patterns.
"""
import re
from typing import List, Dict, Tuple, Optional


# ─────────────────────────────────────────────────────────────
# Common medical units - demonstrates: tuple (immutable sequence)
# ─────────────────────────────────────────────────────────────
COMMON_UNITS = (
    'g/dL', 'mg/dL', 'mmol/L', 'µmol/L', 'umol/L', 'mEq/L', 'IU/L', 'U/L',
    'ng/mL', 'pg/mL', 'µg/dL', 'ug/dL', 'ng/dL', 'µIU/mL', 'uIU/mL',
    '/µL', '/uL', '/mm³', '/mm3', 'cells/µL', 'thou/µL', 'K/µL',
    '%', 'fL', 'pg', 'g/L', 'mmHg', 'bpm', 'kg/m²', 'mg/L',
    'mIU/L', 'nmol/L', 'pmol/L', 'mU/L', 'μg/L', 'μmol/L',
    'seconds', 'sec', 'ratio', 'index', 'titre', 'titer',
)

# Build regex-safe unit pattern - demonstrates string joining and list comprehension
UNIT_PATTERN = '|'.join(
    re.escape(u) for u in sorted(COMMON_UNITS, key=len, reverse=True)
)

# ─────────────────────────────────────────────────────────────
# Main regex patterns for extracting test results
# Demonstrates: raw strings, regex groups, patterns
# ─────────────────────────────────────────────────────────────
TEST_PATTERNS = [
    # Pattern 1: "Test Name    12.5   g/dL   10.0 - 17.0"  (tabular format)
    re.compile(
        r'^([A-Za-z][A-Za-z0-9\s\(\)/,-]{2,50}?)\s+'
        r'([\d.]+)\s+'
        r'(' + UNIT_PATTERN + r')\s*'
        r'(?:([\d.]+\s*[-–]\s*[\d.]+|[<>]\s*[\d.]+))?',
        re.MULTILINE | re.IGNORECASE
    ),
    # Pattern 2: "Test Name: 12.5 g/dL (Ref: 10.0-17.0)"
    re.compile(
        r'([A-Za-z][A-Za-z0-9\s\(\)/,-]{2,50}?)\s*:\s*'
        r'([\d.]+)\s*'
        r'(' + UNIT_PATTERN + r')\s*'
        r'(?:\(?\s*(?:ref(?:erence)?|normal|range)?\s*:?\s*([\d.]+\s*[-–]\s*[\d.]+|[<>]\s*[\d.]+)\s*\)?)?',
        re.IGNORECASE
    ),
    # Pattern 3: "Hemoglobin 13.5 (Normal: 12.0 - 16.0) g/dL"
    re.compile(
        r'([A-Za-z][A-Za-z0-9\s\(\)/,-]{2,50}?)\s+'
        r'([\d.]+)\s*'
        r'(?:\(?\s*(?:normal|ref)\s*:?\s*([\d.]+\s*[-–]\s*[\d.]+)\s*\)?)?\s*'
        r'(' + UNIT_PATTERN + r')',
        re.IGNORECASE
    ),
    # Pattern 4: Simple "Name Value" without unit (less reliable)
    re.compile(
        r'^([A-Za-z][A-Za-z0-9\s\(\)/,-]{4,40}?)\s{2,}'
        r'([\d]+\.?\d*)\s*$',
        re.MULTILINE
    ),
]

# Reference range extraction patterns
REF_RANGE_PATTERNS = [
    re.compile(r'([\d.]+)\s*[-–]\s*([\d.]+)'),    # 10.0 - 17.0
    re.compile(r'<\s*([\d.]+)'),                    # < 200
    re.compile(r'>\s*([\d.]+)'),                    # > 40
    re.compile(r'up\s+to\s+([\d.]+)', re.IGNORECASE),
]

# Known medical test names to improve matching precision
KNOWN_TESTS = {
    # Hematology
    'hemoglobin', 'haemoglobin', 'hematocrit', 'haematocrit',
    'rbc count', 'wbc count', 'platelet count', 'mcv', 'mch', 'mchc', 'rdw',
    'neutrophils', 'lymphocytes', 'monocytes', 'eosinophils', 'basophils',
    'esr', 'reticulated count',
    # Biochemistry
    'glucose', 'fasting glucose', 'blood glucose', 'hba1c',
    'creatinine', 'urea', 'bun', 'uric acid', 'sodium', 'potassium',
    'chloride', 'bicarbonate', 'total protein', 'albumin', 'globulin',
    'total bilirubin', 'direct bilirubin', 'indirect bilirubin',
    'alt', 'sgpt', 'ast', 'sgot', 'alkaline phosphatase', 'gamma gt',
    'total cholesterol', 'triglycerides', 'hdl cholesterol', 'ldl cholesterol',
    'vldl', 'calcium', 'phosphorus', 'magnesium',
    # Thyroid
    'tsh', 't3', 't4', 'free t3', 'free t4',
    # Vitamins/Iron
    'vitamin d', 'vitamin b12', 'folate', 'iron', 'tibc', 'ferritin',
    # Other
    'psa', 'crp', 'esr', 'ra factor', 'ast', 'insulin',
}


def extract_test_results(text: str) -> List[Dict]:
    """
    Extract medical test results from text using regular expressions.

    Demonstrates: regex, loops, lists, dictionaries, string methods,
                  functions, branching, tuples

    Args:
        text: Raw extracted text from medical document

    Returns:
        List of dictionaries with test information
    """
    results = []
    seen_tests = set()  # Set to track duplicates

    if not text:
        return results

    # Clean text slightly for better matching
    clean = _preprocess_text(text)

    # Try each pattern - demonstrates loops over tuples/lists
    for pattern in TEST_PATTERNS:
        matches = pattern.findall(clean)

        for match in matches:
            result = _parse_match(match, pattern)
            if result is None:
                continue

            test_name = result['test_name']
            normalized = test_name.lower().strip()

            # Skip if already found (set lookup O(1))
            if normalized in seen_tests:
                continue

            # Validate the extracted result
            if _is_valid_result(result):
                seen_tests.add(normalized)
                results.append(result)

    # Sort by test name alphabetically
    results.sort(key=lambda x: x['test_name'].lower())

    return results


def _preprocess_text(text: str) -> str:
    """
    Clean text for better regex matching.
    Demonstrates: string methods, loops, branching
    """
    lines = []
    for line in text.split('\n'):
        # Normalize multiple spaces to tab-like spacing
        line = re.sub(r'\s{3,}', '   ', line)
        # Remove lines that are clearly headers or page numbers
        stripped = line.strip()
        if len(stripped) < 2:
            continue
        if re.match(r'^\d+$', stripped):
            continue
        lines.append(line)

    return '\n'.join(lines)


def _parse_match(match: tuple, pattern: re.Pattern) -> Optional[Dict]:
    """
    Parse a regex match tuple into a structured dictionary.
    Demonstrates: tuple indexing, dictionaries, branching, string methods
    """
    if not match or len(match) < 2:
        return None

    try:
        # Pattern has different group orderings - handle each
        if pattern is TEST_PATTERNS[2]:
            # Pattern 3 stores its reference range before its unit.
            test_name = match[0].strip()
            value_str = match[1].strip()
            ref_range = match[2].strip() if match[2] else ''
            unit = match[3].strip() if len(match) > 3 else ''
        elif len(match) >= 3:
            test_name = match[0].strip()
            value_str = match[1].strip()
            unit = match[2].strip() if len(match) > 2 else ''
            ref_range = match[3].strip() if len(match) > 3 and match[3] else ''
        else:
            test_name = match[0].strip()
            value_str = match[1].strip()
            unit = ''
            ref_range = ''

        # Parse numeric value
        numeric_value = _parse_numeric(value_str)

        return {
            'test_name': _clean_test_name(test_name),
            'value': value_str,
            'unit': unit,
            'reference_range': ref_range,
            'numeric_value': numeric_value,
        }
    except (IndexError, AttributeError, ValueError):
        return None


def _clean_test_name(name: str) -> str:
    """
    Clean and normalize test name.
    Demonstrates: string methods, regex, branching
    """
    # Remove leading/trailing whitespace and punctuation
    name = name.strip().strip(':-.,')
    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name)
    # Title case for display
    return name.title()


def _parse_numeric(value_str: str) -> Optional[float]:
    """
    Parse a string value to float.
    Demonstrates: branching, type conversion, exception handling
    """
    if not value_str:
        return None
    try:
        # Remove commas (e.g., "8,500" -> "8500")
        clean = value_str.replace(',', '').strip()
        return float(clean)
    except (ValueError, AttributeError):
        return None


def _is_valid_result(result: Dict) -> bool:
    """
    Validate an extracted test result.
    Demonstrates: branching, string methods, boolean logic
    """
    name = result.get('test_name', '')
    value = result.get('value', '')
    numeric = result.get('numeric_value')

    # Must have a name and value
    if not name or not value:
        return False

    # Name should be reasonable length
    if len(name) < 2 or len(name) > 80:
        return False

    # Filter out common false positives
    false_positives = {
        'date', 'page', 'lab', 'ref', 'normal', 'range', 'value',
        'result', 'test', 'unit', 'specimen', 'sample',
    }
    if name.lower().strip() in false_positives:
        return False

    # Numeric value should be reasonable for medical context
    if numeric is not None:
        if numeric < 0 or numeric > 1_000_000:
            return False

    return True


def extract_dates_from_text(text: str) -> List[str]:
    """
    Extract date mentions from text.
    Demonstrates: regex, list comprehension, string operations
    """
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}',
    ]

    dates = []
    for pattern in date_patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(found)

    # Remove duplicates while preserving order
    seen = set()
    unique_dates = []
    for d in dates:
        if d not in seen:
            seen.add(d)
            unique_dates.append(d)

    return unique_dates


def extract_lab_observations(text: str) -> List[str]:
    """
    Extract qualitative observations (High, Low, Abnormal, etc.) from text.
    Demonstrates: regex, list operations, string methods
    """
    observation_patterns = [
        r'([A-Za-z\s]+?)\s*[:-]\s*(High|Low|Abnormal|Normal|Elevated|Decreased|Positive|Negative|Borderline)',
        r'(High|Low|Abnormal|Elevated|Decreased)\s*[:-]?\s*([A-Za-z\s]+)',
    ]

    observations = []
    for pattern in observation_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Tuple unpacking - demonstrates tuple operations
            item, status = match[0].strip(), match[1].strip()
            if item and status and len(item) < 60:
                observations.append(f"{item}: {status.title()}")

    return list(set(observations))  # Remove duplicates using set


def get_text_statistics(text: str) -> Dict:
    """
    Get basic statistics about the extracted text.
    Demonstrates: string methods, dictionaries, functions, numerical operations
    """
    if not text:
        return {'word_count': 0, 'line_count': 0, 'char_count': 0}

    words = text.split()
    lines = [l for l in text.split('\n') if l.strip()]

    return {
        'word_count': len(words),
        'line_count': len(lines),
        'char_count': len(text),
        'has_numbers': bool(re.search(r'\d', text)),
        'has_units': any(unit.lower() in text.lower() for unit in COMMON_UNITS[:10]),
    }
