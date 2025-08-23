# app/extensions.py
"""
This file initializes shared extensions to prevent circular import errors between the main
app and its blueprints/models
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()