import unittest
import requests

class TestAPI(unittest.TestCase):
    BASE_URL = "http://localhost:8000"  # Change to your API's base URL

    def test_root_endpoint(self):
        response = requests.get(f"{self.BASE_URL}/")
        self.assertEqual(response.status_code, 200)

    def test_predict_endpoint(self):
        # Example for a POST endpoint, adjust as needed
        files = {'file': ('test.jpg', open('test.jpg', 'rb'), 'image/jpeg')}
        response = requests.post(f"{self.BASE_URL}/predict", files=files)
        self.assertEqual(response.status_code, 200)
        self.assertIn("result", response.json())

if __name__ == "__main__":
    unittest.main()