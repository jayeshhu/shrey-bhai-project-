"""
MediScan AI - Demo Data Generator
Provides realistic demo/sample medical data for presentations
Demonstrates: dictionaries, lists, functions, branching
"""
from typing import Dict, List


# Demo CBC (Complete Blood Count) data
DEMO_CBC_TEXT = """
PATHOLOGY LABORATORY - MEDICAL REPORT
Patient Name: Demo Patient
Age: 35 Years    Sex: Male
Date: 01/10/2024
Report ID: DEMO-2024-CBC-001

COMPLETE BLOOD COUNT (CBC)

Test Name               Result      Reference Range     Units
Hemoglobin              14.2        13.0 - 17.0         g/dL
RBC Count               5.1         4.5 - 5.9           million/µL
WBC Count               7800        4000 - 11000        /µL
Platelet Count          245000      150000 - 400000     /µL
Hematocrit              42.5        40.0 - 52.0         %
MCV                     83          80 - 100            fL
MCH                     28.5        27.0 - 32.0         pg
MCHC                    33.5        32.0 - 36.0         g/dL
RDW                     13.2        11.5 - 14.5         %

DIFFERENTIAL COUNT
Neutrophils             65          50 - 70             %
Lymphocytes             28          20 - 40             %
Monocytes               5           2 - 8               %
Eosinophils             2           1 - 4               %
Basophils               0           0 - 1               %

IMPRESSION: Values within normal reference ranges.
This is DEMO data for educational purposes only.
"""

# Demo Biochemistry panel
DEMO_BIOCHEMISTRY_TEXT = """
CLINICAL BIOCHEMISTRY REPORT
Patient: Demo Patient (F/28)
Date: 01/10/2024

LIPID PROFILE
Total Cholesterol        185         < 200              mg/dL
Triglycerides            140         < 150              mg/dL
HDL Cholesterol          52          > 40               mg/dL
LDL Cholesterol          105         < 130              mg/dL
VLDL                     28          < 30               mg/dL

LIVER FUNCTION TESTS
Total Bilirubin          0.8         0.2 - 1.2          mg/dL
Direct Bilirubin         0.2         0.0 - 0.3          mg/dL
ALT (SGPT)               28          7 - 40             U/L
AST (SGOT)               25          10 - 40            U/L
Alkaline Phosphatase     75          44 - 147           U/L
Total Protein            7.2         6.4 - 8.3          g/dL
Albumin                  4.1         3.4 - 5.0          g/dL

KIDNEY FUNCTION
Creatinine               0.9         0.6 - 1.2          mg/dL
Urea (BUN)               18          7 - 25             mg/dL
Uric Acid                5.2         3.5 - 7.2          mg/dL

BLOOD GLUCOSE
Fasting Glucose          95          70 - 100           mg/dL
HbA1c                    5.4         4.0 - 5.6          %

This is DEMO data for educational purposes only.
"""

# Demo test result dictionaries for CBC
DEMO_CBC_RESULTS = [
    {'test_name': 'Hemoglobin', 'value': '14.2', 'unit': 'g/dL',
     'reference_range': '13.0 - 17.0', 'numeric_value': 14.2},
    {'test_name': 'Rbc Count', 'value': '5.1', 'unit': 'million/µL',
     'reference_range': '4.5 - 5.9', 'numeric_value': 5.1},
    {'test_name': 'Wbc Count', 'value': '7800', 'unit': '/µL',
     'reference_range': '4000 - 11000', 'numeric_value': 7800.0},
    {'test_name': 'Platelet Count', 'value': '245000', 'unit': '/µL',
     'reference_range': '150000 - 400000', 'numeric_value': 245000.0},
    {'test_name': 'Hematocrit', 'value': '42.5', 'unit': '%',
     'reference_range': '40.0 - 52.0', 'numeric_value': 42.5},
    {'test_name': 'Mcv', 'value': '83', 'unit': 'fL',
     'reference_range': '80 - 100', 'numeric_value': 83.0},
    {'test_name': 'Mch', 'value': '28.5', 'unit': 'pg',
     'reference_range': '27.0 - 32.0', 'numeric_value': 28.5},
    {'test_name': 'Mchc', 'value': '33.5', 'unit': 'g/dL',
     'reference_range': '32.0 - 36.0', 'numeric_value': 33.5},
    {'test_name': 'Neutrophils', 'value': '65', 'unit': '%',
     'reference_range': '50 - 70', 'numeric_value': 65.0},
    {'test_name': 'Lymphocytes', 'value': '28', 'unit': '%',
     'reference_range': '20 - 40', 'numeric_value': 28.0},
]

# Demo test results for biochemistry
DEMO_BIO_RESULTS = [
    {'test_name': 'Total Cholesterol', 'value': '185', 'unit': 'mg/dL',
     'reference_range': '< 200', 'numeric_value': 185.0},
    {'test_name': 'Triglycerides', 'value': '140', 'unit': 'mg/dL',
     'reference_range': '< 150', 'numeric_value': 140.0},
    {'test_name': 'Hdl Cholesterol', 'value': '52', 'unit': 'mg/dL',
     'reference_range': '> 40', 'numeric_value': 52.0},
    {'test_name': 'Ldl Cholesterol', 'value': '105', 'unit': 'mg/dL',
     'reference_range': '< 130', 'numeric_value': 105.0},
    {'test_name': 'Fasting Glucose', 'value': '95', 'unit': 'mg/dL',
     'reference_range': '70 - 100', 'numeric_value': 95.0},
    {'test_name': 'Hba1C', 'value': '5.4', 'unit': '%',
     'reference_range': '4.0 - 5.6', 'numeric_value': 5.4},
    {'test_name': 'Creatinine', 'value': '0.9', 'unit': 'mg/dL',
     'reference_range': '0.6 - 1.2', 'numeric_value': 0.9},
    {'test_name': 'Alt (Sgpt)', 'value': '28', 'unit': 'U/L',
     'reference_range': '7 - 40', 'numeric_value': 28.0},
    {'test_name': 'Total Bilirubin', 'value': '0.8', 'unit': 'mg/dL',
     'reference_range': '0.2 - 1.2', 'numeric_value': 0.8},
    {'test_name': 'Total Protein', 'value': '7.2', 'unit': 'g/dL',
     'reference_range': '6.4 - 8.3', 'numeric_value': 7.2},
]

# Demo AI summary responses
DEMO_AI_SUMMARIES = {
    'cbc': {
        'summary': (
            "This is a Complete Blood Count (CBC) report for a demo patient. "
            "The blood cell parameters shown are all within their respective reference ranges "
            "as indicated in this report. This is sample data for educational demonstration."
        ),
        'important_findings': [
            "Hemoglobin (14.2 g/dL) is within the provided reference range of 13.0-17.0 g/dL.",
            "WBC Count (7800/µL) is within the provided reference range of 4000-11000/µL.",
            "Platelet Count (245,000/µL) is within the provided reference range.",
            "Differential count parameters are within provided reference ranges.",
            "NOTE: This is DEMO data only. Real reports require professional medical interpretation.",
        ],
        'document_type': 'Blood Report (CBC)',
        'questions_for_doctor': [
            "What do my blood cell counts indicate about my overall health?",
            "Is there any trend I should monitor in these values over time?",
            "Are there dietary or lifestyle factors that could improve these values?",
        ],
        'safety_note': (
            "This is demo/educational data only. Real medical reports must be interpreted "
            "by a qualified healthcare professional. Do not make medical decisions based on this demo."
        ),
        'ai_configured': False,
    },
    'biochemistry': {
        'summary': (
            "This is a biochemistry panel report for a demo patient showing lipid profile, "
            "liver function tests, kidney function, and blood glucose levels. "
            "This is sample data used for educational demonstration purposes."
        ),
        'important_findings': [
            "Lipid panel values are within provided reference ranges.",
            "Liver function tests (ALT, AST, Bilirubin) are within provided reference ranges.",
            "Kidney function markers (Creatinine, BUN) are within provided reference ranges.",
            "Fasting glucose (95 mg/dL) and HbA1c (5.4%) are within provided reference ranges.",
            "NOTE: This is DEMO data only. Real reports require professional medical interpretation.",
        ],
        'document_type': 'Laboratory Report (Biochemistry)',
        'questions_for_doctor': [
            "What does my cholesterol profile mean for my cardiovascular health?",
            "Should I make any dietary changes based on these results?",
            "How often should I repeat these tests?",
        ],
        'safety_note': (
            "This is demo/educational data only. Real medical reports must be interpreted "
            "by a qualified healthcare professional. Do not make medical decisions based on this demo."
        ),
        'ai_configured': False,
    },
}


def get_demo_report(demo_type: str = 'cbc') -> Dict:
    """
    Get a complete demo report dataset.
    Demonstrates: dictionaries, branching, functions

    Args:
        demo_type: 'cbc' or 'biochemistry'

    Returns:
        Dictionary with all demo data
    """
    # Demonstrates: branching with dictionaries
    demos = {
        'cbc': {
            'filename': 'DEMO_CBC_Blood_Report.pdf',
            'document_type': 'Blood Report (CBC)',
            'extracted_text': DEMO_CBC_TEXT,
            'test_results': DEMO_CBC_RESULTS,
            'ai_response': DEMO_AI_SUMMARIES['cbc'],
            'description': 'Complete Blood Count (CBC) Demo Report',
        },
        'biochemistry': {
            'filename': 'DEMO_Biochemistry_Panel.pdf',
            'document_type': 'Laboratory Report',
            'extracted_text': DEMO_BIOCHEMISTRY_TEXT,
            'test_results': DEMO_BIO_RESULTS,
            'ai_response': DEMO_AI_SUMMARIES['biochemistry'],
            'description': 'Biochemistry Panel Demo Report',
        },
    }

    return demos.get(demo_type, demos['cbc'])


def get_all_demo_types() -> List[Dict]:
    """
    Return list of available demo types.
    Demonstrates: lists, dictionaries
    """
    return [
        {
            'key': 'cbc',
            'name': 'Complete Blood Count (CBC)',
            'description': 'Blood cell count parameters',
            'icon': '🩸',
        },
        {
            'key': 'biochemistry',
            'name': 'Biochemistry Panel',
            'description': 'Lipid, liver, kidney, glucose tests',
            'icon': '🔬',
        },
    ]
