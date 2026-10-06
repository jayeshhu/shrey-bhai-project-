"""
MediScan AI - Report Routes
Demonstrates: Flask, file upload, OCR, Pandas, Matplotlib, database operations,
              multithreading, OOP, error handling, security
"""
import os
import json
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, current_app, send_file, jsonify, abort
)
from flask_login import login_required, current_user
from models.database import db, MedicalReport, TestResult, AnalysisHistory
from services.document_processor import process_document
from services.document_classifier import classify_document, extract_patient_info
from services.medical_extractor import extract_test_results, extract_dates_from_text
from services.data_analyzer import MedicalDataAnalyzer, compare_reports
from services.visualizer import (
    generate_test_bar_chart, generate_comparison_chart, generate_status_donut_chart
)
from services.ai_service import ai_service
from services.demo_data import get_demo_report, get_all_demo_types
from config import Config

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─────────────────────────────────────────────────────────────
# Report List
# ─────────────────────────────────────────────────────────────
@reports_bp.route('/reports')
@login_required
def list_reports():
    """Show all reports for current user"""
    reports = MedicalReport.query.filter_by(
        user_id=current_user.id
    ).order_by(MedicalReport.created_at.desc()).all()

    return render_template('reports.html', reports=reports)


# ─────────────────────────────────────────────────────────────
# Upload Page
# ─────────────────────────────────────────────────────────────
@reports_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Upload and process a medical report.
    Demonstrates: file upload, validation, processing pipeline, multithreading
    """
    demo_types = get_all_demo_types()

    if request.method == 'POST':
        # Check if file was submitted
        if 'file' not in request.files:
            flash('No file selected. Please choose a file to upload.', 'error')
            return render_template('upload.html', demo_types=demo_types)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected.', 'error')
            return render_template('upload.html', demo_types=demo_types)

        # Validate file
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload PDF, PNG, JPG, or JPEG files only.', 'error')
            return render_template('upload.html', demo_types=demo_types)

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)     # Reset

        if file_size > MAX_FILE_SIZE:
            flash(f'File is too large ({file_size // (1024*1024):.1f} MB). Maximum size is 10 MB.', 'error')
            return render_template('upload.html', demo_types=demo_types)

        # Save file securely
        original_name = file.filename
        extension = original_name.rsplit('.', 1)[1].lower()
        stored_name = f"{uuid.uuid4().hex}.{extension}"

        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, stored_name)

        try:
            file.save(file_path)
        except Exception as e:
            flash('Failed to save file. Please try again.', 'error')
            logger.error(f"File save error: {e}")
            return render_template('upload.html', demo_types=demo_types)

        # Create database record
        report = MedicalReport(
            user_id=current_user.id,
            original_filename=secure_filename(original_name),
            stored_filename=stored_name,
            analysis_status='processing',
        )
        db.session.add(report)
        db.session.commit()

        # Process the document
        try:
            _process_report(report, file_path, extension)
            flash('Report uploaded and analyzed successfully!', 'success')
        except Exception as e:
            logger.error(f"Report processing error: {e}", exc_info=True)
            report.analysis_status = 'failed'
            db.session.commit()
            flash('Report was uploaded but analysis encountered an error. Partial results may be available.', 'warning')

        return redirect(url_for('reports.report_detail', report_id=report.id))

    return render_template('upload.html', demo_types=demo_types)


def _process_report(report: MedicalReport, file_path: str, extension: str) -> None:
    """
    Full document processing pipeline.
    Demonstrates: multithreading, functions, exception handling, OOP
    """
    import concurrent.futures

    # Step 1: Extract text from document
    logger.info(f"Processing report {report.id}: {report.original_filename}")
    proc_result = process_document(file_path, extension)

    extracted_text = proc_result.get('extracted_text', '')
    extraction_method = proc_result.get('extraction_method', 'none')

    report.extracted_text = extracted_text

    if not extracted_text:
        report.extracted_text = (
            f"[Text extraction attempted using {extraction_method} but no readable text was found. "
            "The document may be encrypted, password-protected, or in an unsupported format.]"
        )

    # Step 2: Classify document
    doc_type, confidence, icon = classify_document(extracted_text)
    report.document_type = doc_type

    # Step 3: Extract test results using regex
    test_results_data = extract_test_results(extracted_text)

    # Step 4: Save test results to database
    for tr_data in test_results_data:
        tr = TestResult(
            report_id=report.id,
            test_name=tr_data.get('test_name', ''),
            value=str(tr_data.get('value', '')),
            unit=tr_data.get('unit', ''),
            reference_range=tr_data.get('reference_range', ''),
            numeric_value=tr_data.get('numeric_value'),
        )
        db.session.add(tr)

    db.session.commit()

    # Step 5: Analyze with Pandas/NumPy
    analyzer = MedicalDataAnalyzer(test_results_data)
    status_breakdown = analyzer.get_status_breakdown()

    # Step 6: Generate charts (can run parallel with AI call)
    charts_folder = current_app.config.get('CHARTS_FOLDER',
                        os.path.join(current_app.root_path, 'static', 'generated_charts'))

    def generate_charts():
        labels, values = analyzer.get_tests_for_chart()
        statuses = []
        for label in labels:
            for tr in test_results_data:
                if tr['test_name'].lower() in label.lower():
                    status = _quick_status(tr)
                    statuses.append(status)
                    break
            else:
                statuses.append('unknown')

        chart_path = None
        if labels and values:
            chart_path = generate_test_bar_chart(
                labels, values, statuses,
                title=f"Test Results - {report.document_type}",
                charts_folder=charts_folder,
            )
        return chart_path

    def call_ai():
        return ai_service.analyze_report(
            test_results_data,
            doc_type,
            extra_context=extracted_text[:300],
        )

    # Use threading for chart gen + AI call simultaneously
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        chart_future = executor.submit(generate_charts)
        ai_future = executor.submit(call_ai)

        chart_path = None
        ai_response = {}
        try:
            chart_path = chart_future.result(timeout=30)
        except Exception as e:
            logger.warning(f"Chart generation failed: {e}")

        try:
            ai_response = ai_future.result(timeout=45)
        except Exception as e:
            logger.warning(f"AI call failed: {e}")
            ai_response = ai_service._get_error_response(str(e))

    # Step 7: Store AI results
    report.ai_summary = ai_response.get('summary', '')
    report.ai_findings = json.dumps(ai_response.get('important_findings', []))
    report.ai_questions = json.dumps(ai_response.get('questions_for_doctor', []))
    report.ai_safety_note = ai_response.get('safety_note', '')
    report.chart_path = chart_path or ''
    report.analysis_status = 'completed'

    db.session.commit()
    logger.info(f"Report {report.id} processing complete")


def _quick_status(tr: dict) -> str:
    """Quick status check for chart coloring"""
    import re
    ref = tr.get('reference_range', '')
    numeric = tr.get('numeric_value')

    if not ref or numeric is None:
        return 'unknown'

    range_match = re.search(r'([\d.]+)\s*[-–]\s*([\d.]+)', ref)
    if range_match:
        try:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
            return 'normal' if low <= numeric <= high else 'review'
        except ValueError:
            pass
    lt_match = re.search(r'<\s*([\d.]+)', ref)
    if lt_match:
        try:
            return 'normal' if numeric < float(lt_match.group(1)) else 'review'
        except ValueError:
            pass
    gt_match = re.search(r'>\s*([\d.]+)', ref)
    if gt_match:
        try:
            return 'normal' if numeric > float(gt_match.group(1)) else 'review'
        except ValueError:
            pass
    return 'unknown'


# ─────────────────────────────────────────────────────────────
# Demo Report
# ─────────────────────────────────────────────────────────────
@reports_bp.route('/demo/<demo_type>')
@login_required
def create_demo(demo_type: str):
    """
    Create a demo report from sample data.
    Demonstrates: functions, dictionaries, database operations
    """
    if demo_type not in ('cbc', 'biochemistry'):
        flash('Invalid demo type.', 'error')
        return redirect(url_for('reports.upload'))

    demo_data = get_demo_report(demo_type)
    ai_response = demo_data['ai_response']

    # Create demo report record
    report = MedicalReport(
        user_id=current_user.id,
        original_filename=demo_data['filename'],
        stored_filename=f"demo_{demo_type}_{uuid.uuid4().hex[:8]}.pdf",
        document_type=demo_data['document_type'],
        extracted_text=demo_data['extracted_text'],
        ai_summary=ai_response.get('summary', ''),
        ai_findings=json.dumps(ai_response.get('important_findings', [])),
        ai_questions=json.dumps(ai_response.get('questions_for_doctor', [])),
        ai_safety_note=ai_response.get('safety_note', ''),
        analysis_status='demo',
        is_demo=True,
    )
    db.session.add(report)
    db.session.flush()  # Get report.id before commit

    # Add demo test results
    charts_folder = current_app.config['CHARTS_FOLDER']
    test_data = demo_data['test_results']

    for tr_data in test_data:
        tr = TestResult(
            report_id=report.id,
            test_name=tr_data['test_name'],
            value=tr_data['value'],
            unit=tr_data['unit'],
            reference_range=tr_data['reference_range'],
            numeric_value=tr_data['numeric_value'],
        )
        db.session.add(tr)

    db.session.commit()

    # Generate chart for demo
    analyzer = MedicalDataAnalyzer(test_data)
    labels, values = analyzer.get_tests_for_chart()
    statuses = [_quick_status(tr) for tr in test_data[:len(labels)]]

    if labels:
        chart_path = generate_test_bar_chart(
            labels, values, statuses,
            title=f"{demo_data['document_type']} - Test Results",
            charts_folder=charts_folder,
        )
        if chart_path:
            report.chart_path = chart_path
            db.session.commit()

    flash(f"Demo report loaded: {demo_data['description']}", 'success')
    return redirect(url_for('reports.report_detail', report_id=report.id))


# ─────────────────────────────────────────────────────────────
# Report Detail
# ─────────────────────────────────────────────────────────────
@reports_bp.route('/reports/<int:report_id>')
@login_required
def report_detail(report_id: int):
    """
    Show detailed report analysis.
    Demonstrates: authorization, database relationships, JSON parsing
    """
    report = MedicalReport.query.get_or_404(report_id)

    # Authorization check - users can only see their own reports
    if report.user_id != current_user.id:
        abort(403)

    # Get test results
    test_results = TestResult.query.filter_by(report_id=report.id).all()
    test_dicts = [tr.to_dict() for tr in test_results]

    # Parse JSON fields
    ai_findings = []
    ai_questions = []
    try:
        if report.ai_findings:
            ai_findings = json.loads(report.ai_findings)
    except (json.JSONDecodeError, TypeError):
        ai_findings = []
    try:
        if report.ai_questions:
            ai_questions = json.loads(report.ai_questions)
    except (json.JSONDecodeError, TypeError):
        ai_questions = []

    # Analyze data
    analyzer = MedicalDataAnalyzer(test_dicts)
    status_breakdown = analyzer.get_status_breakdown()

    # Patient info from text
    patient_info = extract_patient_info(report.extracted_text or '')

    # Analysis history (Q&A)
    history = AnalysisHistory.query.filter_by(
        report_id=report.id
    ).order_by(AnalysisHistory.created_at.asc()).all()

    # Other user reports for comparison selector
    other_reports = MedicalReport.query.filter(
        MedicalReport.user_id == current_user.id,
        MedicalReport.id != report.id,
        MedicalReport.analysis_status.in_(['completed', 'demo'])
    ).order_by(MedicalReport.created_at.desc()).limit(10).all()

    return render_template(
        'report_detail.html',
        report=report,
        test_results=test_results,
        test_dicts=test_dicts,
        ai_findings=ai_findings,
        ai_questions=ai_questions,
        status_breakdown=status_breakdown,
        patient_info=patient_info,
        history=history,
        other_reports=other_reports,
        ai_configured=Config.is_ai_configured(),
    )


# ─────────────────────────────────────────────────────────────
# Delete Report
# ─────────────────────────────────────────────────────────────
@reports_bp.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id: int):
    """Delete a report and associated files"""
    report = MedicalReport.query.get_or_404(report_id)

    if report.user_id != current_user.id:
        abort(403)

    # Delete uploaded file if not demo
    if not report.is_demo:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        file_path = os.path.join(upload_folder, report.stored_filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    # Delete chart if exists
    if report.chart_path:
        chart_full = os.path.join(current_app.static_folder, report.chart_path)
        if os.path.exists(chart_full):
            try:
                os.remove(chart_full)
            except Exception:
                pass

    db.session.delete(report)
    db.session.commit()

    flash('Report deleted successfully.', 'success')
    return redirect(url_for('reports.list_reports'))


# ─────────────────────────────────────────────────────────────
# Compare Reports
# ─────────────────────────────────────────────────────────────
@reports_bp.route('/compare', methods=['GET', 'POST'])
@login_required
def compare():
    """
    Compare two reports side by side.
    Demonstrates: Pandas merge, NumPy calculations, Matplotlib
    """
    user_reports = MedicalReport.query.filter(
        MedicalReport.user_id == current_user.id,
        MedicalReport.analysis_status.in_(['completed', 'demo'])
    ).order_by(MedicalReport.created_at.desc()).all()

    comparison_result = None
    chart_path = None
    report_a = None
    report_b = None

    if request.method == 'POST':
        report_a_id = request.form.get('report_a_id', type=int)
        report_b_id = request.form.get('report_b_id', type=int)

        if not report_a_id or not report_b_id:
            flash('Please select two reports to compare.', 'error')
        elif report_a_id == report_b_id:
            flash('Please select two different reports.', 'error')
        else:
            report_a = MedicalReport.query.get(report_a_id)
            report_b = MedicalReport.query.get(report_b_id)

            # Authorization checks
            if not report_a or report_a.user_id != current_user.id:
                abort(403)
            if not report_b or report_b.user_id != current_user.id:
                abort(403)

            # Get test results
            results_a = [tr.to_dict() for tr in report_a.test_results]
            results_b = [tr.to_dict() for tr in report_b.test_results]

            # Compare using Pandas
            comparison_result = compare_reports(
                results_a, results_b,
                report_a_label=report_a.original_filename[:30],
                report_b_label=report_b.original_filename[:30],
            )

            # Generate comparison chart
            if comparison_result.get('chart_data'):
                charts_folder = current_app.config.get('CHARTS_FOLDER',
                                    os.path.join(current_app.root_path, 'static', 'generated_charts'))
                chart_path = generate_comparison_chart(
                    comparison_result,
                    charts_folder=charts_folder,
                )

    return render_template(
        'compare.html',
        user_reports=user_reports,
        comparison_result=comparison_result,
        chart_path=chart_path,
        report_a=report_a,
        report_b=report_b,
    )


# ─────────────────────────────────────────────────────────────
# Download Report Summary
# ─────────────────────────────────────────────────────────────
@reports_bp.route('/reports/<int:report_id>/download')
@login_required
def download_summary(report_id: int):
    """
    Generate and download a PDF summary of the report.
    Demonstrates: file generation, Python string formatting, branching
    """
    report = MedicalReport.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        abort(403)

    test_results = TestResult.query.filter_by(report_id=report.id).all()
    ai_findings = []
    ai_questions = []
    try:
        if report.ai_findings:
            ai_findings = json.loads(report.ai_findings)
    except Exception:
        pass
    try:
        if report.ai_questions:
            ai_questions = json.loads(report.ai_questions)
    except Exception:
        pass

    # Try to generate PDF with reportlab
    try:
        pdf_path = _generate_pdf_summary(report, test_results, ai_findings, ai_questions)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"MediScan_Summary_{report.id}.pdf",
            mimetype='application/pdf',
        )
    except ImportError:
        # Fallback: generate plain text summary
        txt = _generate_text_summary(report, test_results, ai_findings, ai_questions)
        import io
        buf = io.BytesIO(txt.encode('utf-8'))
        buf.seek(0)
        return send_file(
            buf,
            as_attachment=True,
            download_name=f"MediScan_Summary_{report.id}.txt",
            mimetype='text/plain',
        )


def _generate_text_summary(report, test_results, findings, questions) -> str:
    """Generate plain text report summary"""
    lines = [
        "=" * 60,
        "MEDISCAN AI - REPORT SUMMARY",
        "=" * 60,
        "",
        "DISCLAIMER: This is an informational summary only.",
        "It does not constitute medical advice or diagnosis.",
        "Consult a qualified healthcare professional for medical decisions.",
        "",
        f"Report: {report.original_filename}",
        f"Type: {report.document_type}",
        f"Date: {report.created_at.strftime('%Y-%m-%d %H:%M')}",
        f"Status: {report.analysis_status}",
        "",
        "─" * 60,
        "AI SUMMARY",
        "─" * 60,
        report.ai_summary or "Not available",
        "",
        "─" * 60,
        "TEST RESULTS",
        "─" * 60,
    ]

    if test_results:
        lines.append(f"{'Test Name':<35} {'Value':<12} {'Unit':<12} {'Reference Range'}")
        lines.append("-" * 80)
        for tr in test_results:
            ref = tr.reference_range or 'Not provided'
            lines.append(f"{tr.test_name:<35} {tr.value:<12} {tr.unit:<12} {ref}")
    else:
        lines.append("No structured test data extracted.")

    lines.extend(["", "─" * 60, "KEY OBSERVATIONS", "─" * 60])
    for f in findings:
        lines.append(f"• {f}")

    lines.extend(["", "─" * 60, "QUESTIONS TO DISCUSS WITH YOUR DOCTOR", "─" * 60])
    for q in questions:
        lines.append(f"• {q}")

    lines.extend([
        "",
        "=" * 60,
        "MediScan AI - Educational Tool",
        "Not a substitute for professional medical advice.",
        "=" * 60,
    ])

    return '\n'.join(lines)


def _generate_pdf_summary(report, test_results, findings, questions):
    """Generate a PDF summary in memory for download."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import cm
    from xml.sax.saxutils import escape
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=4,
        spaceBefore=12,
    )

    story = []

    # Title
    story.append(Paragraph("MediScan AI - Report Summary", title_style))
    story.append(Paragraph(
        "<b>DISCLAIMER:</b> Educational and informational tool only. "
        "Not a substitute for professional medical advice.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*cm))

    # Report info
    story.append(Paragraph("Report Information", heading_style))
    info_data = [
        ['Filename:', escape(report.original_filename)],
        ['Document Type:', escape(report.document_type)],
        ['Date:', report.created_at.strftime('%Y-%m-%d %H:%M')],
        ['Status:', report.analysis_status.title()],
    ]
    info_table = Table(info_data, colWidths=[4*cm, 13*cm])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(info_table)

    # AI Summary
    story.append(Paragraph("Summary", heading_style))
    story.append(Paragraph(escape(report.ai_summary or "Not available."), styles['Normal']))

    # Test Results Table
    if test_results:
        story.append(Paragraph("Extracted Test Results", heading_style))
        t_data = [['Test Name', 'Value', 'Unit', 'Reference Range']]
        for tr in test_results:
            t_data.append([
                escape(tr.test_name),
                escape(tr.value),
                escape(tr.unit),
                escape(tr.reference_range or 'Not provided'),
            ])
        t = Table(t_data, colWidths=[6*cm, 3*cm, 3*cm, 5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dbeafe')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        story.append(t)

    # Findings
    if findings:
        story.append(Paragraph("Key Observations", heading_style))
        for f in findings:
            story.append(Paragraph(f"• {f}", styles['Normal']))

    # Questions
    if questions:
        story.append(Paragraph("Questions to Discuss with Your Doctor", heading_style))
        for q in questions:
            story.append(Paragraph(f"• {q}", styles['Normal']))

    # Footer
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Generated by MediScan AI — Educational Tool — Not Medical Advice",
        styles['Normal']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
