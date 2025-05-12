"""
Data serializers for API responses.
"""
from datetime import datetime

def serialize_face(face):
    """
    Serialize a face for API response.
    
    Args:
        face: Face data dictionary
        
    Returns:
        Serialized face dictionary
    """
    # Convert MongoDB _id to id if needed
    face_id = face.get('_id', face.get('id'))
    
    # Format timestamp
    timestamp = face.get('timestamp')
    if isinstance(timestamp, datetime):
        timestamp = timestamp.isoformat()
    
    return {
        'id': face_id,
        'timestamp': timestamp,
        'metadata': face.get('metadata', {})
    }

def serialize_object(obj):
    """
    Serialize an object for API response.
    
    Args:
        obj: Object data dictionary
        
    Returns:
        Serialized object dictionary
    """
    # Convert MongoDB _id to id if needed
    object_id = obj.get('_id', obj.get('id'))
    
    # Format timestamps
    first_seen = obj.get('first_seen')
    if isinstance(first_seen, datetime):
        first_seen = first_seen.isoformat()
    
    last_seen = obj.get('last_seen')
    if isinstance(last_seen, datetime):
        last_seen = last_seen.isoformat()
    
    return {
        'id': object_id,
        'tracking_id': obj.get('tracking_id'),
        'class_name': obj.get('class_name'),
        'owner_id': obj.get('owner_id'),
        'first_seen': first_seen,
        'last_seen': last_seen,
        'metadata': obj.get('metadata', {})
    }

def serialize_detection(detection):
    """
    Serialize a detection for API response.
    
    Args:
        detection: Detection dictionary
        
    Returns:
        Serialized detection dictionary
    """
    serialized = {
        'class_name': detection.get('class_name'),
        'confidence': detection.get('confidence'),
        'bbox': detection.get('bbox')
    }
    
    # Add tracking ID if available
    if 'tracking_id' in detection:
        serialized['tracking_id'] = detection['tracking_id']
    
    # Add face ID if available
    if 'face_id' in detection:
        serialized['face_id'] = detection['face_id']
    
    return serialized