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
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('public.login_page'))

            if role != "any" and session.get('role') != role:
                return "<h1>403 Forbidden: You do not have access to this page.</h1>", 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator