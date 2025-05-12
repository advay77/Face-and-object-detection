"""
Face detection and recognition using YOLO and face_recognition.
"""
import cv2
import numpy as np
import face_recognition
import uuid
import logging
from ultralytics import YOLO

from encryption.encrypt import encrypt_face_data
from detection.utils import filter_detections

logger = logging.getLogger(__name__)

class FaceDetector:
    """Face detection and recognition class."""
    
    def __init__(self, model_path, confidence_threshold=0.5, face_recognition_tolerance=0.6):
        """
        Initialize the face detector.
        
        Args:
            model_path: Path to YOLO model
            confidence_threshold: Minimum confidence for detections
            face_recognition_tolerance: Tolerance for face recognition (lower is stricter)
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.face_recognition_tolerance = face_recognition_tolerance
        self.known_faces = {}  # face_id -> face_encoding
        logger.info("Face detector initialized")
    
    def load_known_faces(self, faces_data):
        """
        Load known faces from database.
        
        Args:
            faces_data: List of face data dictionaries from database
        """
        for face in faces_data:
            if 'encoding' in face and face['encoding'] is not None:
                self.known_faces[face['_id']] = np.array(face['encoding'])
        
        logger.info(f"Loaded {len(self.known_faces)} known faces")
    
    def detect(self, frame):
        """
        Detect and recognize faces in a frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            List of face detections with bounding boxes, IDs, and confidence
        """
        # Run YOLO detection
        results = self.model(frame)
        
        # Filter for person class
        detections = []
        for r in results:
            for detection in r:
                class_id = int(detection.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(detection.conf[0])
                
                if class_name == 'person' and confidence > self.confidence_threshold:
                    x1, y1, x2, y2 = detection.xyxy[0].tolist()
                    
                    detections.append({
                        'class_name': class_name,
                        'class_id': class_id,
                        'confidence': confidence,
                        'bbox': (x1, y1, x2, y2)
                    })
        
        # Process each detected person for face recognition
        for detection in detections:
            x1, y1, x2, y2 = [int(coord) for coord in detection['bbox']]
            
            # Extract person region
            person_img = frame[y1:y2, x1:x2]
            
            if person_img.size == 0:
                continue
            
            # Convert to RGB (face_recognition uses RGB)
            rgb_img = cv2.cvtColor(person_img, cv2.COLOR_BGR2RGB)
            
            # Detect faces in the person region
            face_locations = face_recognition.face_locations(rgb_img)
            
            if face_locations:
                # Get face encodings
                face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
                
                if face_encodings:
                    face_encoding = face_encodings[0]
                    
                    # Try to recognize the face
                    face_id = self._recognize_face(face_encoding)
                    
                    # Add face ID to detection
                    detection['face_id'] = face_id
                    
                    # Add face location relative to the full frame
                    top, right, bottom, left = face_locations[0]
                    detection['face_location'] = (
                        y1 + top, 
                        x1 + left, 
                        y1 + bottom, 
                        x1 + right
                    )
                    
                    # Add face encoding
                    detection['face_encoding'] = face_encoding.tolist()
        
        return detections
    
    def _recognize_face(self, face_encoding):
        """
        Compare face with known faces.
        
        Args:
            face_encoding: Face encoding to compare
            
        Returns:
            face_id if match found, None otherwise
        """
        if not self.known_faces:
            return None
        
        # Compare face with known faces
        matches = face_recognition.compare_faces(
            list(self.known_faces.values()), 
            face_encoding, 
            tolerance=self.face_recognition_tolerance
        )
        
        # If no match found
        if not any(matches):
            return None
        
        # Find the best match
        face_distances = face_recognition.face_distance(
            list(self.known_faces.values()), 
            face_encoding
        )
        best_match_index = np.argmin(face_distances)
        
        if matches[best_match_index]:
            return list(self.known_faces.keys())[best_match_index]
        
        return None
    
    def prepare_face_data(self, frame, detection):
        """
        Prepare face data for storage.
        
        Args:
            frame: Input image frame
            detection: Face detection with face_location and face_encoding
            
        Returns:
            Face data dictionary
        """
        if 'face_location' not in detection or 'face_encoding' not in detection:
            return None
        
        # Extract face image
        top, left, bottom, right = detection['face_location']
        face_image = frame[top:bottom, left:right]
        
        # Generate a unique ID for the face
        face_id = str(uuid.uuid4())
        
        # Encrypt face data
        encrypted_data = encrypt_face_data(face_image)
        
        # Create face data dictionary
        face_data = {
            '_id': face_id,
            'encoding': detection['face_encoding'],
            'encrypted_image': encrypted_data,
            'timestamp': None,  # Will be set by database
            'metadata': {
                'confidence': detection.get('confidence', 0)
            }
        }
        
        return face_data