import unittest
import cv2
import os
import numpy as np
from detection.face_detector import FaceDetector

class TestFaceDetector(unittest.TestCase):
    def setUp(self):
        self.detector = FaceDetector()
        self.test_image_path = os.path.join(os.path.dirname(__file__), 'test_face.jpg')
        # Ensure test image exists or create a dummy one
        if not os.path.exists(self.test_image_path):
            dummy = 255 * np.ones((100, 100, 3), dtype=np.uint8)
            cv2.imwrite(self.test_image_path, dummy)

    def test_detect_faces(self):
        image = cv2.imread(self.test_image_path)
        faces = self.detector.detect_faces(image)
        self.assertIsInstance(faces, list)
        # Optionally, check for expected number of faces
        # self.assertEqual(len(faces), expected_count)

if __name__ == "__main__":
    unittest.main()
