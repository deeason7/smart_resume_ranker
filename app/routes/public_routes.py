# app/routes/public_routes.py
from flask import Blueprint, render_template

# All public-facing routes
public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    """Renders the main landing page."""
    return render_template('index.html')

@public_bp.route('/login')
def login_page():
    """Renders the login page."""
    return render_template('login.html')

@public_bp.route('/signup')
def signup_page():
    """Renders the signup page."""
    return render_template('signup.html')