# app /models/__init__.py
"""
This file makes the 'models' directory a Python package and exposes the model classes for convenient importing elsewhere in the application.
"""
from .user import User
from .job import Job
from .resume import Resume
from .application import Application