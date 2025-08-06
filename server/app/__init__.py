# server/app/__init__.py
# This file contains the application factory for creating the Flask app.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    """Construct the core application."""
    app = Flask(__name__)

    # --- Configuration ---
    # In a real app, this would come from a config.py file or environment variables
    # For now, we'll set it directly.
    # IMPORTANT: Change this secret key in production!
    app.config['SECRET_KEY'] = 'a-very-secret-key-that-you-should-change'
    # Configure the SQLite database, which is a simple file-based database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cloudflower.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_PEPPER'] = 'a-super-long-and-random-string-for-peppering'
    
    # --- Initialize Extensions ---
    # Bind the extensions to the Flask app instance
    db.init_app(app)
    bcrypt.init_app(app)

    # The 'with app.app_context()' is crucial. It makes sure that the application
    # context is available for the imports and registrations below.
    with app.app_context():
        # --- Import and Register Blueprints ---
        # We import here to avoid circular dependencies.
        from . import routes
        
        # Register the blueprint for the API routes
        app.register_blueprint(routes.api, url_prefix='/api')

        # --- Create Database Tables ---
        # This will create the tables based on your models.py file, if they don't exist yet.
        db.create_all()

        return app
