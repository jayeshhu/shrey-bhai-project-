"""
MediScan AI - Authentication Routes
Demonstrates: Flask routing, forms, sessions, password hashing, OOP
"""
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session
)
from flask_login import login_user, logout_user, login_required, current_user
from models.database import db, User

# Create Blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page - demonstrates: Flask routes, form handling, session management
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        # Input validation - demonstrates: branching, string methods
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html')

        # Look up user
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            flash(f'Welcome back, {user.name}!', 'success')
            # Redirect to next page if specified
            next_page = request.args.get('next', '')
            # Restrict post-login redirects to local application paths.
            if not next_page.startswith('/') or next_page.startswith('//'):
                next_page = ''
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration page - demonstrates: form handling, input validation, password hashing
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation - demonstrates: branching, string methods
        errors = _validate_registration(name, email, password, confirm_password)

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html',
                                   name=name, email=email)

        # Check if email already registered
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('This email address is already registered. Please log in.', 'error')
            return render_template('register.html', name=name, email=email)

        # Create new user
        try:
            new_user = User(name=name, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'error')

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logout route - demonstrates: session management, security
    """
    user_name = current_user.name
    logout_user()
    flash(f'You have been logged out successfully. Goodbye, {user_name}!', 'info')
    return redirect(url_for('auth.login'))


def _validate_registration(name: str, email: str,
                            password: str, confirm: str) -> list:
    """
    Validate registration form data.
    Demonstrates: lists, functions, branching, string methods
    """
    errors = []

    if not name or len(name) < 2:
        errors.append('Name must be at least 2 characters long.')

    if not email or '@' not in email or '.' not in email:
        errors.append('Please enter a valid email address.')

    if not password or len(password) < 8:
        errors.append('Password must be at least 8 characters long.')

    if password != confirm:
        errors.append('Passwords do not match.')

    # Check for at least one digit in password
    import re
    if password and not re.search(r'\d', password):
        errors.append('Password must contain at least one number.')

    return errors
