# main.py
import os
import cv2
import numpy as np
import mediapipe as mp
from time import time, strftime
import logging
import facial_recognition as fr

# ----------------- Configuration -----------------
FACE_PICS_DIR = "pictures"          # folder with saved face images (name.jpg -> name)
SAVE_FALL_DIR = "falls"             # where to save snapshot when fall detected
UNKNOWN_FACE_DIR = "unknown_faces"  # where to save unknown faces
FACE_RESIZE = 0.25                  # downscale for face recognition (0.25 = 1/4)
FACE_DISTANCE_THRESHOLD = 0.6       # lower = stricter match
FALL_RATIO_THRESHOLD = 0.20         # fraction of frame height shoulder drop must exceed
FALL_CONSECUTIVE = 2                 # frames in a row to confirm fall
DETECTION_INTERVAL = 1.0             # seconds between fall checks
# --------------------------------------------------

# Prepare directories
os.makedirs(SAVE_FALL_DIR, exist_ok=True)
os.makedirs(FACE_PICS_DIR, exist_ok=True)
os.makedirs(UNKNOWN_FACE_DIR, exist_ok=True)

# Logging setup
logging.basicConfig(
    filename="detections.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Face recognizer
fr_recog = fr.FaceRecognition(
    pictures_dir=FACE_PICS_DIR,
    resize_scale=FACE_RESIZE,
    distance_threshold=FACE_DISTANCE_THRESHOLD
)
fr_recog.encode_faces()

# Mediapipe pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.6, model_complexity=1)

# Fall detector state
baseline_shoulder_y = None
fall_counter = 0
last_check_time = 0

# Video capture
video = cv2.VideoCapture(0)
if not video.isOpened():
    print("[ERROR] Cannot open camera.")
    exit(1)

print("[INFO] Starting video. Press ESC to quit, 's' to save snapshot.")

while True:
    ret, frame = video.read()
    if not ret:
        print("[ERROR] Failed to read frame. Exiting.")
        break

    h, w, _ = frame.shape

    # --- Pose detection ---
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    landmarks = None
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0,128,255), thickness=2)
        )
        landmarks = results.pose_landmarks.landmark

    # --- Face recognition ---
    face_results = fr_recog.recognize_faces(frame)
    for f in face_results:
        (l, t, r, b) = f['bbox']
        name = f['name']

        cv2.rectangle(frame, (l, t), (r, b), (255, 0, 0), 2)
        cv2.putText(frame, name, (l, t - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)

        if name != "Unknown":
            logging.info(f"Face recognized: {name}")
        else:
            logging.warning("Unknown face detected")
            # Save unknown face snapshot
            timestamp = strftime("%Y%m%d_%H%M%S")
            face_img = frame[max(t,0):max(b,0), max(l,0):max(r,0)]
            if face_img.size > 0:
                cv2.imwrite(os.path.join(UNKNOWN_FACE_DIR, f"unknown_{timestamp}.jpg"), face_img)

    # --- Fall detection ---
    now = time()
    fall_detected = False
    if (now - last_check_time) >= DETECTION_INTERVAL:
        last_check_time = now
        if landmarks:
            try:
                left_y = landmarks[11].y * h
                right_y = landmarks[12].y * h
                avg_shoulder_y = (left_y + right_y) / 2.0
            except Exception:
                avg_shoulder_y = None

            if avg_shoulder_y is not None:
                if baseline_shoulder_y is None:
                    baseline_shoulder_y = avg_shoulder_y
                    fall_counter = 0
                else:
                    threshold_px = max(FALL_RATIO_THRESHOLD * h, 60)
                    if (avg_shoulder_y - baseline_shoulder_y) > threshold_px:
                        fall_counter += 1
                    else:
                        fall_counter = 0
                        baseline_shoulder_y = baseline_shoulder_y * 0.98 + avg_shoulder_y * 0.02

                    if fall_counter >= FALL_CONSECUTIVE:
                        fall_detected = True
                        fall_counter = 0
                        baseline_shoulder_y = avg_shoulder_y

    # --- Fall alert ---
    if fall_detected:
        timestamp = strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(SAVE_FALL_DIR, f"fall_{timestamp}.jpg")
        cv2.putText(frame, "FALL DETECTED!", (50, 80), cv2.FONT_HERSHEY_DUPLEX, 2.0, (0,0,255), 4)
        cv2.imwrite(filename, frame)
        logging.critical(f"Fall detected! Snapshot: {filename}")
        print(f"[ALERT] Fall detected! Snapshot saved to {filename}")

    # --- Display ---
    cv2.imshow("Fall + Face", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break
    elif key == ord('s'):
        timestamp = strftime("%Y%m%d_%H%M%S")
        fname = f"snapshot_{timestamp}.jpg"
        cv2.imwrite(fname, frame)
        logging.info(f"Manual snapshot saved: {fname}")
        print("[INFO] Saved snapshot:", fname)

# Cleanup
video.release()
cv2.destroyAllWindows()
pose.close()
