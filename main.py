# main.py
"""
This file is the main entry point for the Flask application.
It creates the application instance and runs the built-in development server.
"""
from app import create_app

# Create the application instance using the default development configuration.
app = create_app()

# Ensures the server only runs when the script is executed directly.
if __name__ == "__main__":
    app.run(debug=True)