"""
Database operations for faces and objects.
"""
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

from app.config import DATABASE
from database.models import Face, Object, Association

logger = logging.getLogger(__name__)

def add_face(db, face_data):
    """
    Add a face to the database.
    
    Args:
        db: Database connection
        face_data: Face data dictionary
        
    Returns:
        Face ID
    """
    try:
        # Ensure ID is present
        if '_id' not in face_data:
            face_data['_id'] = str(uuid.uuid4())
        
        # Ensure timestamp is present
        if 'timestamp' not in face_data:
            face_data['timestamp'] = datetime.now()
        
        if DATABASE['type'] == 'mongodb':
            # MongoDB
            collection = db[DATABASE['collections']['faces']]
            result = collection.insert_one(face_data)
            face_id = face_data['_id']
        else:
            # PostgreSQL
            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO faces (id, encoding, encrypted_image, timestamp, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    face_data['_id'],
                    face_data['encoding'],
                    face_data['encrypted_image'],
                    face_data['timestamp'],
                    face_data.get('metadata', {})
                ))
                face_id = cur.fetchone()['id']
                db.commit()
        
        logger.info(f"Added face {face_id} to database")
        return face_id
    except Exception as e:
        logger.error(f"Error adding face to database: {e}")
        if DATABASE['type'] == 'postgresql':
            db.rollback()
        raise

def get_face(db, face_id):
    """
    Get a face by ID.
    
    Args:
        db: Database connection
        face_id: Face ID
        
    Returns:
        Face data dictionary or None if not found
    """
    try:
        if DATABASE['type'] == 'mongodb':
            # MongoDB
            collection = db[DATABASE['collections']['faces']]
            return collection.find_one({"_id": face_id})
        else:
            # PostgreSQL
            with db.cursor() as cur:
                cur.execute("""
                    SELECT id, encoding, encrypted_image, timestamp, metadata
                    FROM faces
                    WHERE id = %s
                """, (face_id,))
                result = cur.fetchone()
                
                if result:
                    # Convert to MongoDB-like format
                    result['_id'] = result['id']
                    return result
                
                return None
    except Exception as e:
        logger.error(f"Error getting face {face_id}: {e}")
        return None

def get_all_faces(db):
    """
    Get all faces.
    
    Args:
        db: Database connection
        
    Returns:
        List of face data dictionaries
    """
    try:
        if DATABASE['type'] == 'mongodb':
            # MongoDB
            collection = db[DATABASE['collections']['faces']]
            return list(collection.find())
        else:
            # PostgreSQL
            with db.cursor() as cur:
                cur.execute("""
                    SELECT id, encoding, encrypted_image, timestamp, metadata
                    FROM faces
                """)
                results = cur.fetchall()
                
                # Convert to MongoDB-like format
                for result in results:
                    result['_id'] = result['id']
                
                return results
    except Exception as e:
        logger.error(f"Error getting all faces: {e}")
        return []

def add_object(db, object_data):
    """
    Add an object to the database.
    
    Args:
        db: Database connection
        object_data: Object data dictionary
        
    Returns:
        Object ID
    """
    try:
        # Ensure ID is present
        if '_id' not in object_data:
            object_data['_id'] = str(uuid.uuid4())
        
        # Ensure timestamps are present
        if 'first_seen' not in object_data:
            object_data['first_seen'] = datetime.now()
        
        if 'last_seen' not in object_data:
            object_data['last_seen'] = datetime.now()
        
        if DATABASE['type'] == 'mongodb':
            # MongoDB
            collection = db[DATABASE['collections']['objects']]
            result = collection.insert_one(object_data)
            object_id = object_data['_id']
        else:
            # PostgreSQL
            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO objects (id, tracking_id, class_name, owner_id, first_seen, last_seen, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    object_data['_id'],
                    object_data['tracking_id'],
                    object_data['class_name'],
                    object_data.get('owner_id'),
                    object_data['first_seen'],
                    object_data['last_seen'],
                    object_data.get('metadata', {})
                ))
                object_id = cur.fetchone()['id']
                db.commit()
        
        logger.info(f"Added object {object_id} to database")
        return object_id
    except Exception as e:
        logger.error(f"Error adding object to database: {e}")
        if DATABASE['type'] == 'postgresql':
            db.rollback()
        raise

def update_object(db, tracking_id, update_data):
    """
    Update an object.
    
    Args:
        db: Database connection
        tracking_id: Object tracking ID
        update_data: Dictionary of fields to update
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if DATABASE['type'] == 'mongodb':
            # MongoDB
            collection = db[DATABASE['collections']['objects']]
            result = collection.update_one({"tracking_id": tracking_id}, {"$set": update_data})
            success = result.modified_count > 0
        else:
            # PostgreSQL
            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(tracking_id)
            
            with db.cursor() as cur:
                cur.execute(f"""
                    UPDATE objects
                    SET {set_clause}
                    WHERE tracking_id = %s
                """, values)
                success = cur.rowcount > 0
                db.commit()
        
        if success:
            logger.info(f"Updated object {tracking_id}")
        else:
            logger.warning(f"Object {tracking_id} not found or not modified")
            
        return success
    except Exception as e:
        logger.error(f"Error updating object {tracking_id}: {e}")
        if DATABASE['type'] == 'postgresql':
            db.rollback()
        return False

def get_object(db, tracking_id):
    """
    Get an object by tracking ID.
    
    Args:
        db: Database connection
        tracking_id: Object tracking ID
        
    Returns:
        Object data dictionary or None if not found
    """
    try:
        if DATABASE['type'] == 'mongodb':
            # MongoDB
            collection = db[DATABASE['collections']['objects']]
            return collection.find_one({"tracking_id": tracking_id})
        else:
            # PostgreSQL
            with db.cursor() as cur:
                cur.execute("""
                    SELECT id, tracking_id, class_name, owner_id, first_seen, last_seen, metadata
                    FROM objects
                    WHERE tracking_id = %s
                """, (tracking_id,))
                result = cur.fetchone()
                
                if result:
                    # Convert to MongoDB-like format
                    result['_id'] = result['id']
                    return result
                
                return None
    except Exception as e:
        logger.error(f"Error getting object {tracking_id}: {e}")
        return None

def get_person_objects(db, person_id):
    """
    Get all objects belonging to a person.
    
    Args:
        db: Database connection
        person_id: Person ID
        
    Returns:
        List of object data dictionaries
    """
    try:
        if DATABASE['type'] == 'mongodb':
            # MongoDB
            collection = db[DATABASE['collections']['objects']]
            return list(collection.find({"owner_id": person_id}))
        else:
            # PostgreSQL
            with db.cursor() as cur:
                cur.execute("""
                    SELECT id, tracking_id, class_name, owner_id, first_seen, last_seen, metadata
                    FROM objects
                    WHERE owner_id = %s
                """, (person_id,))
                results = cur.fetchall()
                
                # Convert to MongoDB-like format
                for result in results:
                    result['_id'] = result['id']
                
                return results
    except Exception as e:
        logger.error(f"Error getting objects for person {person_id}: {e}")
        return []

def add_association(db, association_data):
    """
    Add an object-person association to the database.
    
    Args:
        db: Database connection
        association_data: Association data dictionary
        
    Returns:
        Association ID
    """
    try:
        # Ensure timestamp is present
        if 'timestamp' not in association_data:
            association_data['timestamp'] = datetime.now()
        
        if DATABASE['type'] == 'mongodb':
            # MongoDB
            collection = db[DATABASE['collections']['associations']]
            result = collection.insert_one(association_data)
            association_id = result.inserted_id
        else:
            # PostgreSQL
            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO associations (person_id, object_id, distance, timestamp)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (person_id, object_id) DO UPDATE
                    SET distance = EXCLUDED.distance, timestamp = EXCLUDED.timestamp
                    RETURNING id
                """, (
                    association_data['person_id'],
                    association_data['object_id'],
                    association_data['distance'],
                    association_data['timestamp']
                ))
                association_id = cur.fetchone()['id']
                db.commit()
        
        logger.info(f"Added association to database")
        return association_id
    except Exception as e:
        logger.error(f"Error adding association to database: {e}")
        if DATABASE['type'] == 'postgresql':
            db.rollback()
        raise