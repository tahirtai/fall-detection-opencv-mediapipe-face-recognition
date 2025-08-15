Fall Detection using OpenCV and MediaPipe
Quick Start

1. Clone the repository

git clone https://github.com/tahirtai/fall-detection-opencv-mediapipe-face-recognition.git
cd fall-detection-opencv-mediapipe-face-recognition


2. Create & activate virtual environment (Windows)

python -m venv venv
.\venv\Scripts\activate


3. Install dependencies

pip install --upgrade pip
pip install -r requirements.txt


4. Run the application

python main.py

Project Overview

This project is a real-time fall detection system developed using OpenCV and MediaPipe in Python. It monitors individuals through a live video feed, detects potential falls based on body movement patterns, and triggers alerts with contextual information. The system can also perform face recognition to identify individuals and fetch their medical and emergency details.

Requirements

You need the following installed to run this project:

Python 3.x

OpenCV (cv2)

MediaPipe (mediapipe)

face_recognition

time (built-in Python module)

Install manually if needed:

pip install opencv-python
pip install mediapipe
pip install face_recognition

How It Works
1. Video Capture

Live video feed is captured using OpenCV, enabling continuous real-time monitoring.

2. Landmark Detection

MediaPipe detects human body landmarks such as shoulders, elbows, and hips for movement tracking.

3. Fall Detection Algorithm

The system checks the previous coordinates of the shoulders every few seconds. A significant drop in shoulder height is interpreted as a potential fall.

4. Face Recognition

face_recognition is used to identify the individual in the frame and fetch their information from the database.

5. Alert Triggering

When a fall is detected:

"Fall Detected" is printed on screen.

The individual's medical history, emergency contact details, and care instructions are retrieved.

6. Healthcare & Guardian Integration

The database stores sensitive information securely and sends instant notifications to healthcare authorities and guardians via Telegram, allowing immediate response.

Working Demo

Watch Demo Video

About

Fall Detection using OpenCV, MediaPipe Pose Estimation, and Face Recognition
Designed for healthcare emergency alerts and real-time monitoring.
