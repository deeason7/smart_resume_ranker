# config.py
"""
This file manages the configuration settings for the Flask application.
"""
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from the .env file located in the project root.
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """
    Base configuration class. Contains settings common to all environments.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'qscderfvtybjuji839nji9chhh34fhnuvih3v9nfebuv83nr9ucs8unv')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
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