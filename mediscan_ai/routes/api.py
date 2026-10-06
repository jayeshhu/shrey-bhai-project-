"""
MediScan AI - API Routes (AJAX endpoints)
Demonstrates: Flask JSON API, error handling, session, OOP
"""
import json
import logging
from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from models.database import db, MedicalReport, AnalysisHistory
from services.ai_service import ai_service
from config import Config

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

MAX_QUESTION_LENGTH = 500


@api_bp.route('/api/ask', methods=['POST'])
@login_required
def ask_question():
    """
    AJAX endpoint: Ask a question about a specific report.
    Demonstrates: JSON API, networking, exception handling, dictionaries
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid request body'}), 400

    report_id = data.get('report_id')
    question = data.get('question', '').strip()

    # Validation
    if not report_id:
        return jsonify({'error': 'report_id is required'}), 400
    if not question:
        return jsonify({'error': 'question is required'}), 400
    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify({'error': f'Question too long (max {MAX_QUESTION_LENGTH} characters)'}), 400

    # Get report and authorize
    report = MedicalReport.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    if report.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Build context from report
    report_context = _build_report_context(report)

    # Get AI answer
    try:
        answer = ai_service.answer_question(question, report_context)
    except Exception as e:
        logger.error(f"API ask error: {e}")
        answer = (
            "Unable to process your question at this time. "
            "Please try again later or consult a healthcare professional."
        )

    # Store in history
    try:
        history_entry = AnalysisHistory(
            user_id=current_user.id,
            report_id=report.id,
            question=question,
            answer=answer,
        )
        db.session.add(history_entry)
        db.session.commit()
    except Exception as e:
        logger.error(f"History save error: {e}")
        db.session.rollback()

    return jsonify({
        'question': question,
        'answer': answer,
        'ai_configured': Config.is_ai_configured(),
    })


@api_bp.route('/api/report/<int:report_id>/status')
@login_required
def report_status(report_id: int):
    """Get report processing status"""
    report = MedicalReport.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        abort(403)

    return jsonify({
        'status': report.analysis_status,
        'document_type': report.document_type,
        'test_count': len(report.test_results),
    })


@api_bp.route('/api/ai-status')
@login_required
def ai_status():
    """Check AI configuration status"""
    info = Config.get_ai_info()
    return jsonify(info)


def _build_report_context(report: MedicalReport) -> str:
    """
    Build a text context string from report data for AI questions.
    Demonstrates: string formatting, loops, dictionaries, OOP
    """
    lines = [
        f"Document Type: {report.document_type}",
        f"Analysis Status: {report.analysis_status}",
        "",
    ]

    if report.ai_summary:
        lines.append(f"AI Summary: {report.ai_summary}")
        lines.append("")

    # Add test results
    test_results = report.test_results
    if test_results:
        lines.append("Test Results:")
        for tr in test_results[:20]:
            ref = tr.reference_range or 'Not provided'
            lines.append(f"  - {tr.test_name}: {tr.value} {tr.unit} (Ref: {ref})")

    return '\n'.join(lines)
