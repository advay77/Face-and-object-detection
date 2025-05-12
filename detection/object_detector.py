"""
Object detection and tracking using YOLO.
"""
import cv2
import numpy as np
import uuid
import logging
from ultralytics import YOLO

from detection.utils import filter_detections

logger = logging.getLogger(__name__)

class ObjectDetector:
    """Object detection and tracking class."""
    
    def __init__(self, model_path, confidence_threshold=0.5, iou_threshold=0.5, max_age=30):
        """
        Initialize the object detector.
        
        Args:
            model_path: Path to YOLO model
            confidence_threshold: Minimum confidence for detections
            iou_threshold: Minimum IoU for tracking
            max_age: Maximum number of frames an object can be lost before being removed
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.tracked_objects = {}  # object_id -> object_data
        
        # Object classes we're interested in (excluding person)
        self.target_classes = [
            'backpack', 'umbrella', 'handbag', 'suitcase', 'laptop'
        ]
        
        logger.info("Object detector initialized")
    
    def detect(self, frame):
        """
        Detect and track objects in a frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            List of object detections with bounding boxes, tracking IDs, and confidence
        """
        # Run YOLO detection
        results = self.model(frame)
        
        # Filter for target classes
        detections = []
        for r in results:
            for detection in r:
                class_id = int(detection.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(detection.conf[0])
                
                if class_name in self.target_classes and confidence > self.confidence_threshold:
                    x1, y1, x2, y2 = detection.xyxy[0].tolist()
                    
                    detections.append({
                        'class_name': class_name,
                        'class_id': class_id,
                        'confidence': confidence,
                        'bbox': (x1, y1, x2, y2)
                    })
        
        # Track objects
        tracked_detections = self._track_objects(detections)
        
        return tracked_detections
    
    def _track_objects(self, detections):
        """
        Track objects across frames.
        
        Args:
            detections: List of object detections
            
        Returns:
            List of tracked object detections with tracking IDs
        """
        # Increment age of all tracked objects
        for obj_id in self.tracked_objects:
            self.tracked_objects[obj_id]['age'] += 1
        
        # Match detections to tracked objects
        matched_indices = []
        unmatched_detections = []
        
        for i, detection in enumerate(detections):
            best_match = None
            best_iou = self.iou_threshold
            
            for obj_id, obj_data in self.tracked_objects.items():
                # Only match objects of the same class
                if obj_data['class_name'] != detection['class_name']:
                    continue
                    
                iou = self._calculate_iou(obj_data['bbox'], detection['bbox'])
                
                if iou > best_iou:
                    best_iou = iou
                    best_match = obj_id
            
            if best_match is not None:
                # Update matched object
                self.tracked_objects[best_match]['bbox'] = detection['bbox']
                self.tracked_objects[best_match]['confidence'] = detection['confidence']
                self.tracked_objects[best_match]['age'] = 0
                
                # Add tracking ID to detection
                detection['tracking_id'] = best_match
                matched_indices.append(best_match)
            else:
                unmatched_detections.append(i)
        
        # Create new tracked objects for unmatched detections
        for i in unmatched_detections:
            obj_id = str(uuid.uuid4())
            
            self.tracked_objects[obj_id] = {
                'class_name': detections[i]['class_name'],
                'class_id': detections[i]['class_id'],
                'bbox': detections[i]['bbox'],
                'confidence': detections[i]['confidence'],
                'age': 0,
                'frames_tracked': 1
            }
            
            # Add tracking ID to detection
            detections[i]['tracking_id'] = obj_id
        
        # Remove old tracked objects
        obj_ids_to_remove = []
        for obj_id, obj_data in self.tracked_objects.items():
            if obj_data['age'] > self.max_age:
                obj_ids_to_remove.append(obj_id)
                
        for obj_id in obj_ids_to_remove:
            del self.tracked_objects[obj_id]
        
        return detections
    
    def _calculate_iou(self, bbox1, bbox2):
        """
        Calculate Intersection over Union (IoU) between two bounding boxes.
        
        Args:
            bbox1: First bounding box (x1, y1, x2, y2)
            bbox2: Second bounding box (x1, y1, x2, y2)
            
        Returns:
            IoU value
        """
        # Calculate intersection
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        if x2 < x1 or y2 < y1:
            return 0.0
            
        intersection = (x2 - x1) * (y2 - y1)
        
        # Calculate areas
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        
        # Calculate IoU
        union = area1 + area2 - intersection
        iou = intersection / union if union > 0 else 0
        
        return iou