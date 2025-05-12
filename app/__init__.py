"""
Face and Object Detection System main application package.
"""
import os
import logging
from logging.handlers import RotatingFileHandler

def create_app():
    """Initialize the application."""
    # Create necessary directories
    os.makedirs('static/faces', exist_ok=True)
    os.makedirs('static/objects', exist_ok=True)
    
    # Configure logging
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = os.path.join(log_dir, 'app.log')
    
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger(__name__)
    logger.info("Application initialized")
    
    return logger