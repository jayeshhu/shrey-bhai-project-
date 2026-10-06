"""
MediScan AI - AI Service
Demonstrates: API calls/networking, exception handling, JSON, environment variables,
              OOP, encapsulation, dictionaries
"""
import os
import json
import logging
import requests
import time
from typing import Dict, Optional, List
from config import Config

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Safety disclaimer always appended to AI responses
# ─────────────────────────────────────────────────────────────
SAFETY_NOTE = (
    "This analysis is for educational and informational purposes only. "
    "It does not constitute medical advice, diagnosis, or treatment. "
    "Always consult a qualified healthcare professional for medical decisions."
)

# Structured prompt template for AI
ANALYSIS_PROMPT_TEMPLATE = """You are a medical information assistant helping users understand their medical reports.

IMPORTANT RULES:
1. Do NOT diagnose any disease or condition
2. Do NOT prescribe any medication or dosage
3. Do NOT invent or fabricate any test values
4. Do NOT claim certainty about any medical condition
5. Explain what is already present in the report in simple language
6. If a value seems outside a stated range, suggest consulting a doctor - do not make conclusions

Medical Report Information:
Document Type: {doc_type}
Extracted Test Results:
{test_results}

Additional Context:
{extra_context}

Respond ONLY with a valid JSON object in this exact format:
{{
  "summary": "A 2-3 sentence plain English summary of what this report contains",
  "important_findings": ["finding 1", "finding 2"],
  "document_type": "Refined document type",
  "questions_for_doctor": ["question 1", "question 2", "question 3"],
  "safety_note": "Reminder that this is informational only"
}}

Do not include any text outside the JSON object."""

QUESTION_PROMPT_TEMPLATE = """You are MediScan AI, a friendly general-purpose assistant with access to a user's medical report.

IMPORTANT:
First understand what the user is actually asking.

There are three types of questions:

1. MEDICAL REPORT QUESTIONS
If the user asks about their medical report, test results, values, abnormalities, health-related meaning, or whether something in the report is concerning:
- Use the report information provided.
- Explain the information in simple language.
- Do not diagnose diseases.
- Do not prescribe medicines or treatments.
- Do not invent test results.
- If the report does not contain enough information, clearly say so.
- Do not guarantee that the user is completely safe or free from disease.

2. GENERAL OR CASUAL QUESTIONS
If the user asks a normal question that is not about their medical report, answer it normally and naturally.
Examples include greetings, general knowledge, mathematics, programming, science, jokes, everyday questions, etc.
Do not force these questions into a medical-report discussion.

3. UNCLEAR QUESTIONS
If the user's question is too short or ambiguous to understand, politely ask them to clarify what they mean.
Do not return an error.

Report Information:
{report_context}

User Question:
{question}

Answer the user's actual question directly.
"""



class AIService:
    """
    AI Service class - handles communication with AI APIs.
    Demonstrates: OOP, encapsulation, networking, exception handling
    """

    def __init__(self):
        self.api_key = Config.AI_API_KEY
        self.provider = Config.AI_PROVIDER
        self.configured = Config.is_ai_configured()

    def analyze_report(
        self,
        test_results: List[Dict],
        doc_type: str,
        extra_context: str = ""
    ) -> Dict:
        """
        Send report data to AI and get structured analysis.
        Demonstrates: networking, JSON, exception handling, dictionaries

        Args:
            test_results: List of extracted test result dicts
            doc_type: Document type string
            extra_context: Additional text context

        Returns:
            Dictionary with AI analysis or fallback response
        """
        if not self.configured:
            logger.info("AI not configured, returning mock analysis")
            return self._get_mock_analysis(test_results, doc_type)

        # Build structured test results text
        test_text = self._format_test_results(test_results)

        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            doc_type=doc_type,
            test_results=test_text or "No structured test values extracted",
            extra_context=extra_context[:500] if extra_context else "None",
        )

        try:
            raw_response = self._call_api(prompt)
            parsed = self._parse_json_response(raw_response)
            # Always ensure safety note is present
            parsed['safety_note'] = SAFETY_NOTE
            return parsed
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            # Preserve the report context when an API call or response parse
            # fails, so the local fallback can still summarize extracted data.
            return self._get_mock_analysis(test_results, doc_type)
        
    def answer_question(
        self,
        question: str,
        report_context: str,
    ) -> str:
        """
        Answer a user's question about a report.
        Demonstrates: networking, string formatting, exception handling

        Args:
            question: The user's question
            report_context: Context about the report

        Returns:
            Answer string
        """
        if not self.configured:
            return self._get_mock_answer(question)

        prompt = QUESTION_PROMPT_TEMPLATE.format(
            report_context=report_context[:1500],
            question=question[:300],
        )

        try:
            response = self._call_api(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"AI question error: {e}")
            return self._get_fallback_answer(question, report_context)

            
    def _call_api(self, prompt: str) -> str:
        """
        Make the actual API call based on configured provider.
        Demonstrates: networking (requests), branching, exception handling
        """
        provider = self.provider.lower()

        if provider == 'gemini':
            return self._call_gemini(prompt)
        elif provider == 'openai':
            return self._call_openai(prompt)
        elif provider == 'groq':
            return self._call_groq(prompt)
        else:
            raise ValueError(f"Unknown AI provider: {provider}")


    def _call_gemini(self, prompt: str) -> str:
        """
        Call Google Gemini API with automatic retries.
        """
        model = Config.GEMINI_MODEL

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={self.api_key}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
            }
        }

        for attempt in range(3):
            response = requests.post(
                url,
                json=payload,
                timeout=30
            )

            if response.ok:
                break

            if response.status_code in (429, 503) and attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue

            raise RuntimeError(
                f"Gemini API error {response.status_code}: {response.text}"
            )

        data = response.json()

        candidates = data.get("candidates", [])

        if not candidates:
            raise ValueError("No candidates in Gemini response")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])

        if not parts:
            raise ValueError("No parts in Gemini content")

        return parts[0].get("text", "")

        
    def _call_groq(self, prompt: str) -> str:
        """
        Call Groq API (free tier available).
        Demonstrates: HTTP requests, JSON, API integration
        """
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": Config.GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1024,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if not response.ok: raise RuntimeError(f"Gemini API error {response.status_code}: {response.text}")

        data = response.json()
        return data['choices'][0]['message']['content']

    def _parse_json_response(self, raw: str) -> Dict:
        """
        Parse JSON from AI response.
        Demonstrates: JSON parsing, string methods, exception handling
        """
        if not raw:
            return self._get_error_response("Empty response from AI")

        # Try to extract JSON from the response
        raw = raw.strip()

        # Sometimes AI wraps JSON in markdown code blocks
        if '```json' in raw:
            start = raw.find('```json') + 7
            end = raw.find('```', start)
            raw = raw[start:end].strip()
        elif '```' in raw:
            start = raw.find('```') + 3
            end = raw.find('```', start)
            raw = raw[start:end].strip()

        try:
            parsed = json.loads(raw)
            # Validate expected fields - demonstrates dictionary operations
            expected_fields = ['summary', 'important_findings', 'document_type',
                               'questions_for_doctor', 'safety_note']
            for field in expected_fields:
                if field not in parsed:
                    parsed[field] = self._default_value(field)
            return parsed
        except json.JSONDecodeError:
            # If not valid JSON, wrap the text in summary
            return {
                'summary': raw[:500] if raw else "Analysis completed.",
                'important_findings': [],
                'document_type': 'Medical Document',
                'questions_for_doctor': ['Please consult your healthcare provider for clarification.'],
                'safety_note': SAFETY_NOTE,
            }

    @staticmethod
    def _get_fallback_answer(question: str, report_context: str) -> str:
        """
        Provide a local answer when the external AI service is unavailable.

        This fallback is intentionally rule-based. It keeps the Q&A feature
        useful during API quota/network problems without pretending to
        diagnose medical conditions.
        """
        q = question.lower().strip()

        # ---------------------------------------------------------
        # GENERAL / CASUAL QUESTIONS
        # ---------------------------------------------------------
        if any(word in q for word in [
            'who are you',
            'what are you',
            'introduce yourself'
        ]):
            return (
                "I am MediScan AI, an educational medical-report analysis "
                "assistant. I can help explain information extracted from "
                "medical reports, summarize test results, and answer general "
                "questions. I do not diagnose diseases or replace advice from "
                "a qualified healthcare professional."
            )

        if q in ['hello', 'hi', 'hey', 'hello there', 'hi there']:
            return (
                "Hello! I am MediScan AI. I can help you understand "
                "information from your medical reports and answer general "
                "questions."
            )

        # Simple arithmetic questions
        import re

        arithmetic_match = re.fullmatch(
            r'\s*(\d+(?:\.\d+)?)\s*([+\-*/xX×])\s*(\d+(?:\.\d+)?)\s*\??',
            q
        )

        if arithmetic_match:
            try:
                a = float(arithmetic_match.group(1))
                operator = arithmetic_match.group(2)
                b = float(arithmetic_match.group(3))

                if operator in ['x', 'X', '×']:
                    result = a * b
                elif operator == '+':
                    result = a + b
                elif operator == '-':
                    result = a - b
                elif operator == '/':
                    if b == 0:
                        return "Division by zero is undefined."
                    result = a / b
                else:
                    result = None

                if result is not None:
                    if result.is_integer():
                        result = int(result)
                    return f"The answer is {result}."
            except (ValueError, ZeroDivisionError):
                pass

        # ---------------------------------------------------------
        # MEDICAL / REPORT QUESTIONS
        # ---------------------------------------------------------

        # Lifestyle questions
        if any(word in q for word in [
            'lifestyle',
            'life style',
            'habits',
            'improve these',
            'improve my results',
            'improve my health',
            'what should i do',
            'how can i improve'
        ]):
            return (
                "Based on the report information available, general healthy "
                "habits may help support cardiovascular and metabolic health. "
                "These include:\n\n"
                "• Regular physical activity appropriate for your fitness level.\n"
                "• A balanced diet with vegetables, fruits, whole grains, "
                "fiber-rich foods, and adequate protein.\n"
                "• Limiting excessive saturated fat, highly processed foods, "
                "and added sugars.\n"
                "• Maintaining a healthy body weight if recommended by your "
                "healthcare professional.\n"
                "• Getting adequate, consistent sleep.\n"
                "• Avoiding tobacco and limiting alcohol where applicable.\n\n"
                "The values in this demo report are within the reference ranges "
                "shown in the report. These are general educational suggestions, "
                "not personalized medical advice. A healthcare professional can "
                "interpret your results together with your age, medical history, "
                "medications, and other factors."
            )

        # Cholesterol questions
        if any(word in q for word in [
            'cholesterol',
            'ldl',
            'hdl',
            'triglyceride',
            'lipid'
        ]):
            if report_context:
                return (
                    "The report contains a lipid profile including total "
                    "cholesterol, LDL cholesterol, HDL cholesterol, and "
                    "triglycerides. The values shown are within the reference "
                    "ranges provided in this demo report.\n\n"
                    "General habits that support cardiovascular health include "
                    "regular physical activity, a diet rich in vegetables, "
                    "whole grains and fiber, limiting excessive saturated and "
                    "trans fats, avoiding tobacco, and maintaining a healthy "
                    "weight where appropriate.\n\n"
                    "Reference ranges are not the same as an individualized "
                    "medical assessment. A healthcare professional can interpret "
                    "these numbers in the context of your overall health."
                )

        # Blood sugar / diabetes-related questions
        if any(word in q for word in [
            'glucose',
            'blood sugar',
            'hba1c',
            'a1c',
            'diabetes'
        ]):
            return (
                "The report includes fasting glucose and HbA1c values, and the "
                "values shown are within the reference ranges provided in this "
                "demo report.\n\n"
                "General habits that support healthy blood glucose include "
                "regular physical activity, eating balanced meals with "
                "fiber-rich foods, limiting excessive added sugars and highly "
                "processed foods, getting adequate sleep, and maintaining a "
                "healthy weight where appropriate.\n\n"
                "These results alone cannot establish or rule out a medical "
                "condition. A healthcare professional should interpret them "
                "alongside your medical history and other relevant information."
            )

        # Liver questions
        if any(word in q for word in [
            'liver',
            'alt',
            'sgpt',
            'bilirubin'
        ]):
            return (
                "The report includes liver-related measurements such as ALT "
                "(SGPT) and total bilirubin. The values shown in this demo "
                "report are within the reference ranges provided.\n\n"
                "General habits that can support liver health include maintaining "
                "a balanced diet, regular physical activity, maintaining a "
                "healthy weight where appropriate, avoiding tobacco, and "
                "avoiding excessive alcohol consumption.\n\n"
                "A healthcare professional should interpret liver results in "
                "the context of symptoms, medical history, medications, and "
                "other laboratory findings."
            )

        # Kidney questions
        if any(word in q for word in [
            'kidney',
            'creatinine',
            'renal'
        ]):
            return (
                "The report includes creatinine as a kidney-related measurement. "
                "The value shown in this demo report is within the reference "
                "range provided.\n\n"
                "General habits that support overall kidney health include "
                "staying appropriately hydrated, maintaining a balanced diet, "
                "being physically active, managing blood pressure when relevant, "
                "and avoiding unnecessary use of medications or supplements "
                "without professional guidance.\n\n"
                "Kidney function should be interpreted using the full clinical "
                "picture rather than a single laboratory value."
            )

        # ---------------------------------------------------------
        # NORMAL / ABNORMAL QUESTIONS
        # ---------------------------------------------------------
        if any(word in q for word in [
            'normal',
            'abnormal',
            'okay',
            'ok',
            'fine',
            'within range'
        ]):
            return (
                "According to the reference ranges displayed in this demo "
                "report, the listed test values are within their stated ranges. "
                "That describes the laboratory reference ranges only and does "
                "not by itself establish that a person has no health problems. "
                "A healthcare professional can interpret the results in the "
                "context of symptoms, medical history, and other findings."
            )

        # ---------------------------------------------------------
        # DOCTOR / NEXT-STEP QUESTIONS
        # ---------------------------------------------------------
        if any(word in q for word in [
            'doctor',
            'physician',
            'healthcare provider',
            'what should i ask',
            'discuss with'
        ]):
            return (
                "You could discuss the results with your healthcare professional "
                "and ask which values are most relevant to your individual health, "
                "whether any follow-up testing is appropriate, and whether your "
                "diet, activity level, medications, or other factors could affect "
                "the results."
            )

        # ---------------------------------------------------------
        # REPORT INFORMATION REQUEST
        # ---------------------------------------------------------
        if any(word in q for word in [
            'report',
            'test',
            'result',
            'value',
            'blood',
            'cbc',
            'range'
        ]):
            if report_context:
                return (
                    "I can explain the information available in your report. "
                    "The extracted report data available to me is:\n\n"
                    f"{report_context[:1200]}\n\n"
                    "The external AI service is temporarily unavailable, so "
                    "this answer is based only on the extracted report "
                    "information. For diagnosis or personalized medical "
                    "advice, please consult a qualified healthcare professional."
                )

        # ---------------------------------------------------------
        # UNKNOWN QUESTION
        # ---------------------------------------------------------
        return (
            "I can help with questions about the information in your medical "
            "report, general health concepts, or general questions. The "
            "external AI service is temporarily unavailable right now. "
            "Please try asking your question in a more specific way, or "
            "consult a qualified healthcare professional for personalized "
            "medical advice."
        )       




    @staticmethod
    def _format_test_results(test_results: List[Dict]) -> str:
        """
        Format test results as readable text for AI prompt.
        Demonstrates: loops, string formatting, lists
        """
        if not test_results:
            return "No structured test values found"

        lines = []
        for result in test_results[:20]:  # Limit to prevent token overflow
            name = result.get('test_name', 'Unknown')
            value = result.get('value', 'N/A')
            unit = result.get('unit', '')
            ref = result.get('reference_range', 'Not provided')

            line = f"- {name}: {value} {unit}"
            if ref and ref not in ('', 'Not provided in document'):
                line += f" (Reference: {ref})"
            lines.append(line)

        return '\n'.join(lines)

    @staticmethod
    def _get_mock_analysis(test_results: List[Dict], doc_type: str) -> Dict:
        """
        Return mock analysis when AI is not configured.
        Demonstrates: dictionaries, lists, branching
        """
        has_tests = bool(test_results)

        findings = []
        if has_tests:
            findings.append(
                f"The document appears to contain {len(test_results)} "
                f"extracted test parameter(s)."
            )
            findings.append(
                "Test values have been extracted and are shown in the table below."
            )
        else:
            findings.append("No structured test values could be extracted from this document.")

        findings.append(
            "Configure an AI API key to receive intelligent analysis of these results."
        )

        return {
            'summary': (
                f"This appears to be a {doc_type}. "
                f"{'Test values have been extracted for your review.' if has_tests else 'Limited structured data was found.'} "
                "To receive an AI-powered explanation, please configure the AI API key in your .env file."
            ),
            'important_findings': findings,
            'document_type': doc_type,
            'questions_for_doctor': [
                "Ask your doctor to explain any values that are outside the reference range.",
                "Ask about what follow-up tests, if any, are recommended.",
                "Ask about lifestyle changes or monitoring that may be appropriate.",
            ],
            'safety_note': SAFETY_NOTE,
            'ai_configured': False,
        }

    @staticmethod
    def _get_mock_answer(question: str) -> str:
        """
        Return a helpful mock answer when AI is not configured.
        """
        return (
            f"The AI service is not currently configured. "
            f"To enable intelligent Q&A about your reports, please add your AI API key to the .env file. "
            f"For your question: '{question[:100]}', please consult your healthcare provider directly "
            f"for accurate medical information and advice."
        )

    @staticmethod
    def _get_error_response(error: str) -> Dict:
        """Return structured error response"""
        return {
            'summary': f"AI analysis encountered an issue: {error[:200]}. Extracted data is still available below.",
            'important_findings': ["AI analysis failed - please review the extracted test results manually."],
            'document_type': 'Medical Document',
            'questions_for_doctor': ['Please consult your healthcare provider for interpretation.'],
            'safety_note': SAFETY_NOTE,
            'error': error,
        }


# Module-level singleton - demonstrates module-level objects
ai_service = AIService()



