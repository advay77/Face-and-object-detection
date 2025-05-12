import unittest
import cv2
import os
import numpy as np
from detection.object_detector import ObjectDetector

class TestObjectDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ObjectDetector()
        self.test_image_path = os.path.join(os.path.dirname(__file__), 'test_object.jpg')
        # Ensure test image exists or create a dummy one
        if not os.path.exists(self.test_image_path):
            dummy = 255 * np.ones((100, 100, 3), dtype=np.uint8)
            cv2.imwrite(self.test_image_path, dummy)

    def test_detect_objects(self):
        image = cv2.imread(self.test_image_path)
        objects = self.detector.detect_objects(image)
        self.assertIsInstance(objects, list)
        # Optionally, check for expected number of objects
        # self.assertEqual(len(objects), expected_count)

if __name__ == "__main__":
    unittest.main()
