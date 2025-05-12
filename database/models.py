"""
Database schema definitions.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional

class Face:
    """Face data model."""
    
    def __init__(self, 
                 id: str,
                 encoding: List[float],
                 encrypted_image: str,
                 timestamp: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a Face object.
        
        Args:
            id: Unique identifier
            encoding: Face encoding vector
            encrypted_image: Encrypted face image data
            timestamp: Time when the face was detected
            metadata: Additional metadata
        """
        self.id = id
        self.encoding = encoding
        self.encrypted_image = encrypted_image
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            '_id': self.id,
            'encoding': self.encoding,
            'encrypted_image': self.encrypted_image,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Face':
        """Create a Face from a dictionary."""
        return cls(
            id=data.get('_id', data.get('id')),
            encoding=data.get('encoding'),
            encrypted_image=data.get('encrypted_image'),
            timestamp=data.get('timestamp'),
            metadata=data.get('metadata', {})
        )


class Object:
    """Object data model."""
    
    def __init__(self,
                 id: str,
                 tracking_id: str,
                 class_name: str,
                 owner_id: Optional[str] = None,
                 first_seen: Optional[datetime] = None,
                 last_seen: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an Object object.
        
        Args:
            id: Unique identifier
            tracking_id: Tracking identifier
            class_name: Object class name
            owner_id: ID of the person who owns this object
            first_seen: Time when the object was first detected
            last_seen: Time when the object was last detected
            metadata: Additional metadata
        """
        self.id = id
        self.tracking_id = tracking_id
        self.class_name = class_name
        self.owner_id = owner_id
        self.first_seen = first_seen or datetime.now()
        self.last_seen = last_seen or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            '_id': self.id,
            'tracking_id': self.tracking_id,
            'class_name': self.class_name,
            'owner_id': self.owner_id,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Object':
        """Create an Object from a dictionary."""
        return cls(
            id=data.get('_id', data.get('id')),
            tracking_id=data.get('tracking_id'),
            class_name=data.get('class_name'),
            owner_id=data.get('owner_id'),
            first_seen=data.get('first_seen'),
            last_seen=data.get('last_seen'),
            metadata=data.get('metadata', {})
        )


class Association:
    """Association between a person and an object."""
    
    def __init__(self,
                 person_id: str,
                 object_id: str,
                 distance: float,
                 timestamp: Optional[datetime] = None):
        """
        Initialize an Association object.
        
        Args:
            person_id: ID of the person
            object_id: ID of the object
            distance: Distance between person and object
            timestamp: Time when the association was made
        """
        self.person_id = person_id
        self.object_id = object_id
        self.distance = distance
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'person_id': self.person_id,
            'object_id': self.object_id,
            'distance': self.distance,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Association':
        """Create an Association from a dictionary."""
        return cls(
            person_id=data.get('person_id'),
            object_id=data.get('object_id'),
            distance=data.get('distance'),
            timestamp=data.get('timestamp')
        )