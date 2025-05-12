"""
Application entry point.
"""
import os
from flask import Flask, render_template
import logging

from app import create_app
from app.config import API
from api.routes import api

# Initialize logging
logger = create_app()

def create_flask_app():
    """Create and configure Flask application."""
    # Create Flask app
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Configure app
    app.config['SECRET_KEY'] = API['secret_key']
    app.config['DEBUG'] = API['debug']
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    # Root route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    # Create Flask app
    app = create_flask_app()
    
    # Run app
    app.run(
        host=API['host'],
        port=API['port'],
        debug=API['debug']
    )