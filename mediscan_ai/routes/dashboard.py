"""
MediScan AI - Dashboard Routes
Demonstrates: Flask routing, login_required, database queries, Pandas
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models.database import MedicalReport, TestResult
from config import Config

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Main dashboard page.
    Demonstrates: database queries, OOP, dictionaries
    """
    # Get user's reports
    reports = MedicalReport.query.filter_by(
        user_id=current_user.id
    ).order_by(MedicalReport.created_at.desc()).all()

    # Calculate stats - demonstrates: list comprehension, filtering
    total_reports = len(reports)
    analyzed_reports = len([r for r in reports if r.analysis_status == 'completed'])
    demo_reports = len([r for r in reports if r.is_demo])

    # Recent reports (last 5)
    recent_reports = reports[:5]

    # Stats cards data - demonstrates: dictionaries, lists
    stats = {
        'total_reports': total_reports,
        'analyzed': analyzed_reports,
        'demo_reports': demo_reports,
        'can_compare': total_reports >= 2,
    }

    ai_info = Config.get_ai_info()

    return render_template(
        'dashboard.html',
        stats=stats,
        recent_reports=recent_reports,
        ai_info=ai_info,
        ai_configured=ai_info['configured'],
    )

@dashboard_bp.route('/about')
@login_required
def about():
    """About page"""
    return render_template('about.html')


@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    User profile page.
    Demonstrates: Flask routes, database operations, form handling
    """
    from flask import request, flash
    from models.database import db

    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        if new_name and len(new_name) >= 2:
            current_user.name = new_name
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        else:
            flash('Name must be at least 2 characters.', 'error')

    # Get user report stats
    reports = MedicalReport.query.filter_by(user_id=current_user.id).all()
    stats = {
        'total_reports': len(reports),
        'completed': len([r for r in reports if r.analysis_status == 'completed']),
    }

    return render_template('profile.html', stats=stats)
