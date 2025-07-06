# config.py
"""
This file manages the configuration settings for the Flask application.

Using a class-based configuration allows for easy switching between different
environments like development, testing, and production.
"""
import os
from dotenv import load_dotenv

# Find the absolute path of the project's root directory.
# This makes the .env file loading reliable, regardless of where the app is run from.
basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from the .env file located in the project root.
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """
    Base configuration class. Contains settings common to all environments.
    """
    # Secret key for signing session cookies and other security-related needs.
    # It's crucial this is kept secret in production. A fallback is provided for development.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'qscderfvtybjuji839nji9chhh34fhnuvih3v9nfebuv83nr9ucs8unv')

    # Disables a resource-intensive feature of Flask-SQLAlchemy that is not needed.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # The database URI. It defaults to a local SQLite database in the 'instance'
    # folder but can be overridden by the DATABASE_URL environment variable for production.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')


class DevelopmentConfig(Config):
    """
    Configuration for the development environment.
    Inherits from the base Config and enables debug mode.
    """
    DEBUG = True


class ProductionConfig(Config):
    """
    Configuration for the production environment.
    Inherits from the base Config and disables debug mode for security and performance.
    """
    DEBUG = False