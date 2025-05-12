"""
Database connection setup.
"""
import logging
import pymongo
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import DATABASE

logger = logging.getLogger(__name__)

def get_database():
    """
    Get database connection based on configuration.
    
    Returns:
        Database connection object
    """
    db_type = DATABASE['type']
    
    if db_type == 'mongodb':
        return get_mongodb_connection()
    elif db_type == 'postgresql':
        return get_postgresql_connection()
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def get_mongodb_connection():
    """
    Get MongoDB connection.
    
    Returns:
        MongoDB database object
    """
    try:
        # Connect to MongoDB
        client = MongoClient(DATABASE['connection_string'])
        db = client[DATABASE['database_name']]
        
        # Create collections if they don't exist
        collections = DATABASE['collections']
        for collection_name in collections.values():
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
        
        # Create indexes
        db[collections['faces']].create_index("timestamp")
        db[collections['objects']].create_index("owner_id")
        db[collections['objects']].create_index("tracking_id")
        db[collections['associations']].create_index([("person_id", 1), ("object_id", 1)])
        
        logger.info(f"Connected to MongoDB: {DATABASE['database_name']}")
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

def get_postgresql_connection():
    """
    Get PostgreSQL connection.
    
    Returns:
        PostgreSQL connection object
    """
    try:
        # Parse connection string
        conn_parts = DATABASE['connection_string'].split('/')
        db_name = DATABASE['database_name']
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            DATABASE['connection_string'],
            cursor_factory=RealDictCursor
        )
        
        # Create tables if they don't exist
        with conn.cursor() as cur:
            # Faces table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS faces (
                    id VARCHAR(36) PRIMARY KEY,
                    encoding JSONB,
                    encrypted_image TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                )
            """)
            
            # Objects table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS objects (
                    id VARCHAR(36) PRIMARY KEY,
                    tracking_id VARCHAR(36) UNIQUE,
                    class_name VARCHAR(50),
                    owner_id VARCHAR(36) REFERENCES faces(id),
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                )
            """)
            
            # Associations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS associations (
                    id SERIAL PRIMARY KEY,
                    person_id VARCHAR(36) REFERENCES faces(id),
                    object_id VARCHAR(36) REFERENCES objects(id),
                    distance FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(person_id, object_id)
                )
            """)
            
            # Create indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_faces_timestamp ON faces(timestamp)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_objects_owner ON objects(owner_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_objects_tracking ON objects(tracking_id)")
            
            conn.commit()
        
        logger.info(f"Connected to PostgreSQL: {db_name}")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise

def close_connection(db):
    """
    Close database connection.
    
    Args:
        db: Database connection object
    """
    if DATABASE['type'] == 'mongodb':
        # MongoDB connections are managed by the client
        pass
    elif DATABASE['type'] == 'postgresql':
        db.close()
        logger.info("Closed PostgreSQL connection")