# app/__init__.py
"""
This file contains the application factory for the Flask app.
It is responsible for initializing the application, its extensions,
and its blueprints.
"""

# Standard library imports
import os

# Third-party imports
from flask import Flask

# Local application imports
from config import DevelopmentConfig
from .extensions import db
from .utils.ui_utils import highlight_keywords


def create_app(config_class=DevelopmentConfig):
    """
    Creates and configures an instance of the Flask application.
    """
    # Application Initialization
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from the specified config object
    app.config.from_object(config_class)
    db.init_app(app)

    # Register Custom Functionality
    app.jinja_env.filters['highlight'] = highlight_keywords

    # Ensure Instance Folders Exist
    try:
        os.makedirs(app.instance_path)
        os.makedirs(os.path.join(app.instance_path, 'uploads/resumes'))
        os.makedirs(os.path.join(app.instance_path, 'ml_models'))
    except OSError:
        pass

    # Register Blueprints and Create Database
    with app.app_context():
        from . import models

        # Import and register all the application's route blueprints
        from .routes import auth_routes, public_routes, recruiter_routes, candidate_routes

        app.register_blueprint(auth_routes.auth_bp)
        app.register_blueprint(public_routes.public_bp)
        app.register_blueprint(recruiter_routes.recruiter_bp)
        app.register_blueprint(candidate_routes.candidate_bp)

        # Create all database tables defined in the models if they don't exist
        db.create_all()

    # Return the fully configured application instance
    return app