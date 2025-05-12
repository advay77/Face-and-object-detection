
# 🎯 Face and Object Detection System 🕵️‍♂️🎥   

> A real-time **Face and Object Detection System** powered by YOLO, providing secure face encryption and seamless object-person association. 🚀

---

## 🌟 **Features**  

✨ **Real-Time Detection**: Leverages YOLO for high-speed and accurate face/object detection.  
🔒 **Secure Face Recognition**: Utilizes encryption to store sensitive data securely.  
🔗 **Object-Person Association**: Tracks objects and associates them with detected individuals.  
🗄️ **Database Integration**: MongoDB/PostgreSQL support for reliable data storage.  
📡 **REST API**: Easy integration with external systems via API endpoints.  
💻 **Web Monitoring**: Interactive web-based UI for live tracking and managing detections.  

---

## 🛠️ **Directory Structure**  

```plaintext
face-object-detection-system/
├── app/                            # Main application package
│   ├── __init__.py
│   ├── config.py                   # Configurations (e.g., secret keys, DB credentials)
│   ├── main.py                     # Entry point for running the app
│
├── detection/                      # Detection logic using YOLO
│   ├── face_detector.py            # YOLO-based face detection
│   ├── object_detector.py          # YOLO-based object detection
│   └── utils.py                    # Helper functions (e.g., draw boxes, filter confidence)
│
├── encryption/                     # Face image encryption and decryption
│   ├── encrypt.py
│   └── decrypt.py
│
├── database/                       # Database interaction logic
│   ├── db.py                       # DB connection setup
│   ├── models.py                   # Schema definitions (Face, Object)
│   └── operations.py               # Insert, retrieve, update logic
│
├── api/                            # REST API
│   ├── routes.py                   # Endpoints for face/object uploads and queries
│   └── serializers.py              # Data formatting/validation
│
├── static/                         # Encrypted face files or images
│   ├── faces/
│   └── objects/
│
├── templates/                      # Web UI templates
│   └── index.html
│
├── test/                           # Test cases
│   ├── test_face.py
│   ├── test_object.py
│   └── test_api.py
│
├── requirements.txt                # Dependencies
├── README.md                       # Documentation
└── run.py                          # Application bootstrap (Flask/FastAPI)
```

---

## 🚀 **Getting Started**  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/advay77/Face-and-object-detection.git
cd Face-and-object-detection
```

### 2️⃣ Install Dependencies  
Ensure you have Python installed, then run:  
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Application  
Start the server:  
```bash
python run.py
```

### 4️⃣ Access the Web App  
Open your browser and navigate to:  
```
http://localhost:5000
```

---

## 🎥 **Live Demo**  

![Detection Demo](https://media.giphy.com/media/3o7TKzsfT2k4xGxMFO/giphy.gif)  

---
## VIDEOS  

https://github.com/user-attachments/assets/947a307d-4821-464f-8b10-6cf4f12a1305
 
## 🎯 **Use Cases**  

- **Security Surveillance**: Real-time monitoring of people and objects in secure zones.  
- **Retail Analytics**: Understand customer interactions with products.  
- **Event Management**: Track attendees and their belongings effortlessly.  

---

## 🧑‍💻 **Contribute**  

We ❤️ contributions! Fork the repo, make your changes, and submit a pull request. Let’s make detection smarter together!  

---

## 📄 **License**  

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  
