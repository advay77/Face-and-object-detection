"""
Application configuration settings.
"""
import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent

# Detection settings
DETECTION = {
    'yolo_model_path': os.environ.get('YOLO_MODEL_PATH', 'models/yolov8n.pt'),
    'confidence_threshold': float(os.environ.get('CONFIDENCE_THRESHOLD', '0.5')),
    'target_classes': [
        'person', 'backpack', 'umbrella', 'handbag', 'suitcase', 'laptop'
    ],
    'face_recognition_tolerance': float(os.environ.get('FACE_RECOGNITION_TOLERANCE', '0.6')),
    'min_face_size': int(os.environ.get('MIN_FACE_SIZE', '20')),
    'face_detection_model': os.environ.get('FACE_DETECTION_MODEL', 'hog')  # 'hog' or 'cnn'
}

# Tracking settings
TRACKING = {
    'iou_threshold': float(os.environ.get('IOU_THRESHOLD', '0.5')),
    'max_age': int(os.environ.get('MAX_AGE', '30')),
    'distance_threshold': int(os.environ.get('DISTANCE_THRESHOLD', '200'))
}

# Database settings
DATABASE = {
    'type': os.environ.get('DB_TYPE', 'mongodb'),  # 'mongodb' or 'postgresql'
    'connection_string': os.environ.get('DB_CONNECTION_STRING', 'mongodb://localhost:27017/'),
    'database_name': os.environ.get('DB_NAME', 'face_object_detection'),
    'collections': {
        'faces': 'faces',
        'objects': 'objects',
        'associations': 'associations'
    }
}

# Encryption settings
ENCRYPTION = {
    'key_file': os.path.join(BASE_DIR, 'static', 'encryption_key.key'),
    'salt_file': os.path.join(BASE_DIR, 'static', 'encryption_salt.key')
}

# API settings
API = {
    'host': os.environ.get('API_HOST', '0.0.0.0'),
    'port': int(os.environ.get('API_PORT', '8000')),
    'debug': os.environ.get('API_DEBUG', 'False').lower() == 'true',
    'secret_key': os.environ.get('API_SECRET_KEY', 'your-secret-key-here')
}

# Static files
STATIC = {
    'faces_dir': os.path.join(BASE_DIR, 'static', 'faces'),
    'objects_dir': os.path.join(BASE_DIR, 'static', 'objects')
}