"""
Encryption utilities for face data.
"""
import cv2
import numpy as np
import base64
from cryptography.fernet import Fernet
import os
import logging

from app.config import ENCRYPTION

logger = logging.getLogger(__name__)

def get_encryption_key():
    """
    Get or generate encryption key.
    
    Returns:
        Encryption key
    """
    key_file = ENCRYPTION['key_file']
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(key_file), exist_ok=True)
    
    if os.path.exists(key_file):
        # Load existing key
        try:
            with open(key_file, "rb") as f:
                key = f.read()
            logger.info(f"Loaded encryption key from {key_file}")
            return key
        except Exception as e:
            logger.error(f"Error loading encryption key: {e}")
            # Fall back to generating a new key
    
    # Generate a new key
    try:
        key = Fernet.generate_key()
        
        # Save the key
        with open(key_file, "wb") as f:
            f.write(key)
        
        logger.info(f"Generated and saved new encryption key to {key_file}")
        return key
    except Exception as e:
        logger.error(f"Error generating encryption key: {e}")
        raise

# Initialize encryption
ENCRYPTION_KEY = get_encryption_key()
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_face_data(face_image):
    """
    Encrypt face image data.
    
    Args:
        face_image: Face image array
        
    Returns:
        Base64 encoded encrypted data
    """
    try:
        # Convert image to bytes
        _, buffer = cv2.imencode('.jpg', face_image)
        image_bytes = buffer.tobytes()
        
        # Encrypt the bytes
        encrypted_data = fernet.encrypt(image_bytes)
        
        # Convert to base64 for storage
        return base64.b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encrypting face data: {e}")
        raise

def encrypt_text(text):
    """
    Encrypt text data.
    
    Args:
        text: Text to encrypt
        
    Returns:
        Base64 encoded encrypted data
    """
    try:
        # Convert text to bytes
        text_bytes = text.encode('utf-8')
        
        # Encrypt the bytes
        encrypted_data = fernet.encrypt(text_bytes)
        
        # Convert to base64 for storage
        return base64.b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encrypting text: {e}")
        raise