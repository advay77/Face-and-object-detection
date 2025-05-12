"""
API routes for the face and object detection system.
"""
import logging
from flask import Blueprint, request, jsonify
import cv2
import numpy as np
import base64
import uuid
from datetime import datetime

from database.db import get_database
from database.operations import (
    add_face, get_face, get_all_faces, 
    add_object, update_object, get_object, get_person_objects
)
from detection.face_detector import FaceDetector
from detection.object_detector import ObjectDetector
from encryption.encrypt import encrypt_face_data
from encryption.decrypt import decrypt_face_data
from api.serializers import serialize_face, serialize_object
from app.config import DATABASE

logger = logging.getLogger(__name__)

# Create blueprint
api = Blueprint('api', __name__)

# Initialize detectors
face_detector = None
object_detector = None

def init_detectors(model_path, confidence_threshold=0.5):
    """Initialize detectors."""
    global face_detector, object_detector
    
    if face_detector is None:
        face_detector = FaceDetector(model_path, confidence_threshold)
    
    if object_detector is None:
        object_detector = ObjectDetector(model_path, confidence_threshold)

@api.route('/faces', methods=['GET'])
def get_faces():
    """Get all faces."""
    try:
        db = get_database()
        faces = get_all_faces(db)
        
        # Serialize faces
        serialized_faces = [serialize_face(face) for face in faces]
        
        return jsonify({
            'status': 'success',
            'count': len(serialized_faces),
            'faces': serialized_faces
        })
    except Exception as e:
        logger.error(f"Error getting faces: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/faces/<face_id>', methods=['GET'])
def get_face_by_id(face_id):
    """Get a face by ID."""
    try:
        db = get_database()
        face = get_face(db, face_id)
        
        if face is None:
            return jsonify({
                'status': 'error',
                'message': f"Face with ID {face_id} not found"
            }), 404
        
        # Serialize face
        serialized_face = serialize_face(face)
        
        return jsonify({
            'status': 'success',
            'face': serialized_face
        })
    except Exception as e:
        logger.error(f"Error getting face {face_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/faces/<face_id>/image', methods=['GET'])
def get_face_image(face_id):
    """Get a face image by ID."""
    try:
        db = get_database()
        face = get_face(db, face_id)
        
        if face is None:
            return jsonify({
                'status': 'error',
                'message': f"Face with ID {face_id} not found"
            }), 404
        
        # Decrypt face image
        face_image = decrypt_face_data(face['encrypted_image'])
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', face_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'face_id': face_id,
            'image': image_base64
        })
    except Exception as e:
        logger.error(f"Error getting face image {face_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/faces', methods=['POST'])
def add_face_route():
    """Add a face."""
    try:
        # Get request data
        data = request.json
        
        if 'image' not in data:
            return jsonify({
                'status': 'error',
                'message': "Image is required"
            }), 400
        
        # Decode image
        image_data = base64.b64decode(data['image'])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({
                'status': 'error',
                'message': "Invalid image data"
            }), 400
        
        # Initialize detectors if needed
        init_detectors('models/yolov8n.pt')
        
        # Detect faces
        face_detections = face_detector.detect(image)
        
        if not face_detections or 'face_encoding' not in face_detections[0]:
            return jsonify({
                'status': 'error',
                'message': "No face detected in the image"
            }), 400
        
        # Prepare face data
        face_data = face_detector.prepare_face_data(image, face_detections[0])
        
        # Add face to database
        db = get_database()
        face_id = add_face(db, face_data)
        
        return jsonify({
            'status': 'success',
            'face_id': face_id,
            'message': "Face added successfully"
        })
    except Exception as e:
        logger.error(f"Error adding face: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/objects', methods=['GET'])
def get_objects():
    """Get all objects."""
    try:
        db = get_database()
        objects = list(db[DATABASE['collections']['objects']].find())
        # Convert MongoDB _id to id for each object
        for obj in objects:
            obj['id'] = str(obj.get('_id', obj.get('id')))
        # Serialize objects
        serialized_objects = [serialize_object(obj) for obj in objects]
        return jsonify({
            'status': 'success',
            'count': len(serialized_objects),
            'objects': serialized_objects
        })
    except Exception as e:
        logger.error(f"Error getting objects: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/objects/<tracking_id>', methods=['GET'])
def get_object_by_id(tracking_id):
    """Get an object by tracking ID."""
    try:
        db = get_database()
        obj = get_object(db, tracking_id)
        
        if obj is None:
            return jsonify({
                'status': 'error',
                'message': f"Object with tracking ID {tracking_id} not found"
            }), 404
        
        # Serialize object
        serialized_object = serialize_object(obj)
        
        return jsonify({
            'status': 'success',
            'object': serialized_object
        })
    except Exception as e:
        logger.error(f"Error getting object {tracking_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/persons/<person_id>/objects', methods=['GET'])
def get_person_objects_route(person_id):
    """Get all objects belonging to a person."""
    try:
        db = get_database()
        objects = get_person_objects(db, person_id)
        
        # Serialize objects
        serialized_objects = [serialize_object(obj) for obj in objects]
        
        return jsonify({
            'status': 'success',
            'count': len(serialized_objects),
            'objects': serialized_objects
        })
    except Exception as e:
        logger.error(f"Error getting objects for person {person_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/detect', methods=['POST'])
def detect():
    """Detect faces and objects in an image."""
    try:
        # Get request data
        data = request.json
        if 'image' not in data:
            return jsonify({
                'status': 'error',
                'message': "Image is required"
            }), 400
        # Decode image
        image_data = base64.b64decode(data['image'])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return jsonify({
                'status': 'error',
                'message': "Invalid image data"
            }), 400
        # Initialize detectors if needed
        init_detectors('models/yolov8n.pt')
        # Detect faces and objects using new YOLOv8 API
        face_results = face_detector.model(image)
        object_results = object_detector.model(image)
        faces = []
        # Parse face detections
        for result in face_results:
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = [float(coord) for coord in box.xyxy[0].tolist()]
                    confidence = float(box.conf[0])
                    face = {
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence
                    }
                    faces.append(face)
        objects = []
        # Parse object detections
        for result in object_results:
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = [float(coord) for coord in box.xyxy[0].tolist()]
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]
                    obj = {
                        'class_name': class_name,
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence
                    }
                    objects.append(obj)
        return jsonify({
            'status': 'success',
            'faces': faces,
            'objects': objects
        })
    except Exception as e:
        logger.error(f"Error detecting faces and objects: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500