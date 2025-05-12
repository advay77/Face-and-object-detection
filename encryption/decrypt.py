"""
Decryption utilities for face data.
"""
import cv2
import numpy as np
import base64
from cryptography.fernet import Fernet
import logging

from encryption.encrypt import ENCRYPTION_KEY

logger = logging.getLogger(__name__)

# Initialize decryption
fernet = Fernet(ENCRYPTION_KEY)

def decrypt_face_data(encrypted_data):
    """
    Decrypt face image data.
    
    Args:
        encrypted_data: Base64 encoded encrypted data
        
    Returns:
        Decrypted face image
    """
    try:
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # Decrypt the data
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        
        # Convert back to image
        nparr = np.frombuffer(decrypted_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return image
    except Exception as e:
        logger.error(f"Error decrypting face data: {e}")
        raise

def decrypt_text(encrypted_data):
    """
    Decrypt text data.
    
    Args:
        encrypted_data: Base64 encoded encrypted data
        
    Returns:
        Decrypted text
    """
    try:
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # Decrypt the data
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        
        # Convert back to text
        text = decrypted_bytes.decode('utf-8')
        
        return text
    except Exception as e:
        logger.error(f"Error decrypting text: {e}")
        raise