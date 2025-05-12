"""
Utility functions for detection and visualization.
"""
import cv2
import numpy as np

def filter_detections(detections, confidence_threshold=0.5, classes=None):
    """
    Filter detections by confidence and class.
    
    Args:
        detections: List of detection dictionaries
        confidence_threshold: Minimum confidence threshold
        classes: List of class names to keep (None for all)
        
    Returns:
        Filtered list of detections
    """
    filtered = []
    
    for detection in detections:
        # Filter by confidence
        if detection['confidence'] < confidence_threshold:
            continue
        
        # Filter by class
        if classes is not None and detection['class_name'] not in classes:
            continue
        
        filtered.append(detection)
    
    return filtered

def draw_boxes(frame, face_detections, object_detections):
    """
    Draw bounding boxes for faces and objects on the frame.
    
    Args:
        frame: Input image frame
        face_detections: List of face detections
        object_detections: List of object detections
        
    Returns:
        Frame with bounding boxes
    """
    # Draw face detections
    for detection in face_detections:
        x1, y1, x2, y2 = [int(coord) for coord in detection['bbox']]
        
        # Draw person bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw face bounding box if available
        if 'face_location' in detection:
            top, left, bottom, right = [int(coord) for coord in detection['face_location']]
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
        
        # Draw label
        label = f"Person {detection['confidence']:.2f}"
        if 'face_id' in detection:
            label += f" ID:{detection['face_id'][:8]}"
        
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw object detections
    for detection in object_detections:
        x1, y1, x2, y2 = [int(coord) for coord in detection['bbox']]
        
        # Draw object bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        # Draw label
        label = f"{detection['class_name']} {detection['confidence']:.2f}"
        if 'tracking_id' in detection:
            label += f" ID:{detection['tracking_id'][:8]}"
        
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    return frame

def extract_face_image(frame, face_location):
    """
    Extract face image from frame.
    
    Args:
        frame: Input image frame
        face_location: Face location (top, left, bottom, right)
        
    Returns:
        Face image
    """
    top, left, bottom, right = face_location
    face_image = frame[top:bottom, left:right]
    return face_image

def resize_image(image, width=None, height=None):
    """
    Resize an image while maintaining aspect ratio.
    
    Args:
        image: Input image
        width: Target width (optional)
        height: Target height (optional)
        
    Returns:
        Resized image
    """
    # Get dimensions
    (h, w) = image.shape[:2]
    
    # If both width and height are None, return original image
    if width is None and height is None:
        return image
    
    # If width is None, calculate it from height
    if width is None:
        r = height / float(h)
        width = int(w * r)
    # If height is None, calculate it from width
    elif height is None:
        r = width / float(w)
        height = int(h * r)
    
    # Resize the image
    resized = cv2.resize(image, (width, height))
    
    return resized