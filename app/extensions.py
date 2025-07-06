# app/extensions.py
"""
This file initializes shared extensions (like the database object) to prevent circular import errors between the main
app and its blueprints/models
"""
from flask_sqlalchemy import SQLAlchemy

# Database instance will be configured and linked to the Flask app later in the application factory.
db = SQLAlchemy()