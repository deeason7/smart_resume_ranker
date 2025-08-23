# main.py
"""
This file is the main entry point for the Flask application.
It creates the application instance and runs the built-in development server.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)