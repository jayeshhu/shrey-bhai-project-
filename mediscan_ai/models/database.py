"""
MediScan AI - Database Models
Demonstrates: OOP, classes, encapsulation, SQLAlchemy ORM, relationships
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy instance
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model - demonstrates: OOP, encapsulation, methods
    Stores user registration and authentication information.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reports = db.relationship('MedicalReport', backref='owner', lazy=True, cascade='all, delete-orphan')
    analysis_history = db.relationship('AnalysisHistory', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        """Hash and store password - never stores plain text"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """Convert user to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'total_reports': len(self.reports),
        }

    def __repr__(self) -> str:
        return f'<User {self.email}>'


class MedicalReport(db.Model):
    """
    Medical Report model - stores uploaded document information.
    Demonstrates: OOP, data structures, string handling
    """
    __tablename__ = 'medical_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(100), default='Unknown')
    extracted_text = db.Column(db.Text, default='')
    ai_summary = db.Column(db.Text, default='')
    ai_findings = db.Column(db.Text, default='')      # JSON string of findings
    ai_questions = db.Column(db.Text, default='')     # JSON string of questions
    ai_safety_note = db.Column(db.Text, default='')
    analysis_status = db.Column(db.String(50), default='pending')
    # Status values: pending, processing, completed, failed, demo
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chart_path = db.Column(db.String(255), default='')

    # Relationships
    test_results = db.relationship('TestResult', backref='report', lazy=True, cascade='all, delete-orphan')
    analysis_history = db.relationship('AnalysisHistory', backref='report', lazy=True, cascade='all, delete-orphan')

    def to_dict(self) -> dict:
        """Convert report to dictionary"""
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'document_type': self.document_type,
            'analysis_status': self.analysis_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_demo': self.is_demo,
            'test_count': len(self.test_results),
        }

    def get_status_badge(self) -> tuple:
        """Return (label, css_class) for status badge"""
        status_map = {
            'pending': ('Pending', 'badge-warning'),
            'processing': ('Processing', 'badge-info'),
            'completed': ('Completed', 'badge-success'),
            'failed': ('Failed', 'badge-danger'),
            'demo': ('Demo', 'badge-demo'),
        }
        return status_map.get(self.analysis_status, ('Unknown', 'badge-secondary'))

    def __repr__(self) -> str:
        return f'<MedicalReport {self.original_filename}>'


class TestResult(db.Model):
    """
    Test Result model - stores extracted medical test values.
    Demonstrates: OOP, numerical data, tuples, string handling
    """
    __tablename__ = 'test_results'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('medical_reports.id'), nullable=False)
    test_name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.String(100), default='')          # Raw value string
    unit = db.Column(db.String(50), default='')
    reference_range = db.Column(db.String(150), default='')
    numeric_value = db.Column(db.Float, nullable=True)     # Parsed numeric value

    def to_dict(self) -> dict:
        """Convert test result to dictionary"""
        return {
            'id': self.id,
            'test_name': self.test_name,
            'value': self.value,
            'unit': self.unit,
            'reference_range': self.reference_range or 'Not provided in document',
            'numeric_value': self.numeric_value,
            'status': self.get_value_status(),
        }

    def get_value_status(self) -> str:
        """
        Determine if value is within reference range.
        NOTE: This only uses ranges explicitly provided in the document.
        Returns: 'normal', 'review', or 'unknown'
        """
        if not self.reference_range or self.numeric_value is None:
            return 'unknown'

        ref = self.reference_range.strip()

        # Try to parse range like "70-100" or "4.5 - 5.5"
        import re
        range_match = re.search(r'([\d.]+)\s*[-–]\s*([\d.]+)', ref)
        if range_match:
            try:
                low = float(range_match.group(1))
                high = float(range_match.group(2))
                if low <= self.numeric_value <= high:
                    return 'normal'
                else:
                    return 'review'
            except ValueError:
                return 'unknown'

        # Try "< X" or "> X" patterns
        lt_match = re.search(r'<\s*([\d.]+)', ref)
        gt_match = re.search(r'>\s*([\d.]+)', ref)
        if lt_match:
            try:
                if self.numeric_value < float(lt_match.group(1)):
                    return 'normal'
                return 'review'
            except ValueError:
                return 'unknown'
        if gt_match:
            try:
                if self.numeric_value > float(gt_match.group(1)):
                    return 'normal'
                return 'review'
            except ValueError:
                return 'unknown'

        return 'unknown'

    def __repr__(self) -> str:
        return f'<TestResult {self.test_name}: {self.value} {self.unit}>'


class AnalysisHistory(db.Model):
    """
    Analysis History - stores Q&A interactions with AI about reports.
    Demonstrates: OOP, string data, datetime handling
    """
    __tablename__ = 'analysis_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('medical_reports.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
        }

    def __repr__(self) -> str:
        return f'<AnalysisHistory report={self.report_id} q={self.question[:30]}>'
