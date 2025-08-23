# app/routes/auth_routes.py
import re
from flask import Blueprint, request, session, redirect, url_for, flash
from app.models import User
from app.helpers import login_required
from app.extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Handles user registration form submission with full validation."""
    data = request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'candidate')

    # Username validation
    if not re.match(r'^\w{3,20}$', username):
        flash('Username must be 3-20 characters long and can only contain letters, numbers, and underscores.', 'danger')
        return redirect(url_for('public.signup_page'))

    # Email validation
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        flash('Please provide a valid email address.', 'danger')
        return redirect(url_for('public.signup_page'))

    # Password complexity validation
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$', password):
        flash('Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one number.', 'danger')
        return redirect(url_for('public.signup_page'))

    if User.query.filter_by(username=username).first():
        flash('This username is already taken. Please choose another.', 'danger')
        return redirect(url_for('public.signup_page'))

    if User.query.filter_by(email=email).first():
        flash('An account with this email already exists.', 'danger')
        return redirect(url_for('public.signup_page'))

    new_user = User(username=username, email=email, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    flash(f"Account created for {new_user.username}! You can now log in.", 'success')
    return redirect(url_for('public.login_page'))

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handles user login form submission."""
    data = request.form
    email, password = data.get('email'), data.get('password')

    if not email or not password:
        flash("Email and password are required.", 'danger')
        return redirect(url_for('public.login_page'))

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        flash("Invalid email or password. Please try again.", 'danger')
        return redirect(url_for('public.login_page'))

    session.clear()
    session['user_id'] = user.id
    session['role'] = user.role

    if user.role == 'recruiter':
        return redirect(url_for('recruiter.dashboard'))
    else:
        return redirect(url_for('candidate.job_list'))

@auth_bp.route('/logout')
@login_required()
def logout():
    """Clears the session and logs the user out."""
    session.clear()
    flash("You have been successfully logged out.", "success")
    return redirect(url_for('public.login_page'))