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

    This function follows the application factory pattern, which is a best
    practice for creating reusable and testable Flask applications.

    Args:
        config_class: The configuration class to use for the app.
                      Defaults to DevelopmentConfig.

    Returns:
        A configured Flask application instance.
    """
    # --- 1. Application Initialization ---
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from the specified config object
    app.config.from_object(config_class)


    # --- 2. Initialize Core Extensions ---
    # Link the SQLAlchemy database object to the Flask app
    db.init_app(app)


    # --- 3. Register Custom Functionality ---
    # Make our custom 'highlight' function available in all Jinja2 templates
    app.jinja_env.filters['highlight'] = highlight_keywords


    # --- 4. Ensure Instance Folders Exist ---
    # This block creates necessary folders on startup if they don't already exist.
    # The `instance` folder is a standard place for files not tracked by Git,
    # like database files and user uploads.
    try:
        os.makedirs(app.instance_path)
        os.makedirs(os.path.join(app.instance_path, 'uploads/resumes'))
        os.makedirs(os.path.join(app.instance_path, 'ml_models'))
    except OSError:
        # This error is expected if the directories already exist, so we can ignore it.
        pass


    # --- 5. Register Blueprints and Create Database ---
    with app.app_context():
        # Importing models here ensures they are registered with SQLAlchemy
        # before the database tables are created.
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