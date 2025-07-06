# app/routes/helpers.py
"""
This module contains helper functions, specifically decorators, used across
the route blueprints to handle common logic like authentication checks.
"""
from functools import wraps
from flask import session, redirect, url_for

def login_required(role="any"):
    """
    A decorator to protect routes that require a user to be logged in.

    It can optionally enforce that the logged-in user has a specific role
    (e.g., 'recruiter' or 'candidate').

    Args:
        role (str): The required role. If "any", it only checks for login.

    Returns:
        The decorated function if the user is authorized, otherwise redirects
        to the login page or shows a 'Forbidden' error.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First, check if a user is logged into the session at all.
            if 'user_id' not in session:
                return redirect(url_for('public.login_page'))

            # If a specific role is required, check it.
            if role != "any" and session.get('role') != role:
                # The user is logged in, but doesn't have the right permissions.
                return "<h1>403 Forbidden: You do not have access to this page.</h1>", 403

            # If all checks pass, proceed to the original route function.
            return f(*args, **kwargs)
        return decorated_function
    return decorator