"""
Main application entry point.
"""
import cv2
import time
import argparse
import logging
import numpy as np
from datetime import datetime

from app import create_app
from app.config import DETECTION, TRACKING, DATABASE
from detection.face_detector import FaceDetector
from detection.object_detector import ObjectDetector
from detection.utils import draw_boxes, filter_detections
from database.db import get_database
from database.operations import add_face, add_object, update_object, get_all_faces
from encryption.encrypt import encrypt_face_data

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Face and Object Detection System')
    
    parser.add_argument('--source', type=str, default='0',
                        help='Video source (0 for webcam, path to video file, or RTSP URL)')
    
    parser.add_argument('--output', type=str, default=None,
                        help='Output video path')
    
    parser.add_argument('--display', action='store_true',
                        help='Display video')
    
    return parser.parse_args()

def process_video(source, output=None, display=False):
    """Process video from the given source."""
    # Initialize detectors
    face_detector = FaceDetector(
        model_path=DETECTION['yolo_model_path'],
        confidence_threshold=DETECTION['confidence_threshold'],
        face_recognition_tolerance=DETECTION['face_recognition_tolerance']
    )
    
    object_detector = ObjectDetector(
        model_path=DETECTION['yolo_model_path'],
        confidence_threshold=DETECTION['confidence_threshold'],
        iou_threshold=TRACKING['iou_threshold'],
        max_age=TRACKING['max_age']
    )
    
    # Initialize database
    db = get_database()
    
    # Load known faces
    known_faces = get_all_faces(db)
    face_detector.load_known_faces(known_faces)
    
    # Open video source
    source = int(source) if source.isdigit() else source
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        logger.error(f"Failed to open video source: {source}")
        return
    
    logger.info(f"Video source opened: {source}")
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Create output video writer if specified
    if output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output, fourcc, fps, (width, height))
        logger.info(f"Output video will be saved to: {output}")
    else:
        out = None
    
    # Process frames
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Read frame
            ret, frame = cap.read()
            
            if not ret:
                logger.info("End of video stream")
                break
            
            # Detect faces
            face_detections = face_detector.detect(frame)
            
            # Detect objects
            object_detections = object_detector.detect(frame)
            
            # Associate objects with faces
            for obj in object_detections:
                if 'tracking_id' not in obj:
                    continue
                
                # Find closest face
                closest_face = None
                min_distance = TRACKING['distance_threshold']
                
                for face in face_detections:
                    if 'face_id' not in face:
                        continue
                    
                    # Calculate distance between face and object
                    face_bbox = face['bbox']
                    obj_bbox = obj['bbox']
                    
                    face_center = ((face_bbox[0] + face_bbox[2]) / 2, (face_bbox[1] + face_bbox[3]) / 2)
                    obj_center = ((obj_bbox[0] + obj_bbox[2]) / 2, (obj_bbox[1] + obj_bbox[3]) / 2)
                    
                    distance = np.sqrt((face_center[0] - obj_center[0])**2 + (face_center[1] - obj_center[1])**2)
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_face = face
                
                # If a close face is found, associate object with face
                if closest_face:
                    # Check if object exists in database
                    existing_obj = db.objects.find_one({"tracking_id": obj['tracking_id']})
                    
                    if existing_obj:
                        # Update object if owner has changed
                        if existing_obj.get('owner_id') != closest_face['face_id']:
                            update_object(db, obj['tracking_id'], {
                                'owner_id': closest_face['face_id'],
                                'last_seen': datetime.now()
                            })
                    else:
                        # Add new object
                        add_object(db, {
                            'tracking_id': obj['tracking_id'],
                            'class_name': obj['class_name'],
                            'owner_id': closest_face['face_id'],
                            'first_seen': datetime.now(),
                            'last_seen': datetime.now()
                        })
            
            # Draw detections on frame
            annotated_frame = draw_boxes(frame.copy(), face_detections, object_detections)
            
            # Write frame to output video
            if out:
                out.write(annotated_frame)
            
            # Display frame
            if display:
                cv2.imshow("Face and Object Detection", annotated_frame)
                
                # Exit on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("User requested exit")
                    break
            
            # Increment frame count
            frame_count += 1
    except KeyboardInterrupt:
        logger.info("User interrupted")
    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
    finally:
        # Calculate processing time and FPS
        processing_time = time.time() - start_time
        processing_fps = frame_count / processing_time if processing_time > 0 else 0
        
        logger.info(f"Processed {frame_count} frames in {processing_time:.2f} seconds ({processing_fps:.2f} FPS)")
        
        # Release resources
        cap.release()
        
        if out:
            out.release()
        
        if display:
            cv2.destroyAllWindows()
        
        logger.info("Processing completed")

def main():
    """Main function."""
    # Initialize app
    create_app()
    
    # Parse arguments
    args = parse_args()
    
    # Process video
    process_video(args.source, args.output, args.display)

if __name__ == "__main__":
    main()