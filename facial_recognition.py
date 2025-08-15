# facial_recognition.py
import os
import cv2
import numpy as np
import face_recognition

class FaceRecognition:
    """
    Simple helper to encode faces from ./pictures and recognize faces in frames.
    Put labeled images in `pictures/` (filename without extension is used as name).
    """

    def __init__(self, pictures_dir='pictures', resize_scale=0.25, distance_threshold=0.50):
        self.pictures_dir = pictures_dir
        self.resize_scale = resize_scale
        self.distance_threshold = distance_threshold
        self.known_faces = []
        self.known_face_names = []

    def encode_faces(self):
        """Scan pictures_dir and create face encodings. Skips images with no detectable face."""
        self.known_faces = []
        self.known_face_names = []
        if not os.path.isdir(self.pictures_dir):
            print(f"[WARN] pictures folder '{self.pictures_dir}' not found. Create it and add images (jpg/png).")
            return

        for fname in os.listdir(self.pictures_dir):
            path = os.path.join(self.pictures_dir, fname)
            if not os.path.isfile(path):
                continue
            try:
                img = face_recognition.load_image_file(path)
                encs = face_recognition.face_encodings(img)
                if not encs:
                    print(f"[WARN] no faces found in '{fname}', skipping.")
                    continue
                self.known_faces.append(encs[0])
                name = os.path.splitext(fname)[0]
                self.known_face_names.append(name)
                print(f"[INFO] encoded '{name}' from {fname}")
            except Exception as e:
                print(f"[ERROR] failed to process '{fname}': {e}")

    def recognize_faces(self, frame):
        """
        Recognize faces in `frame`.
        Returns list of dicts: {'name': str, 'bbox': (left,top,right,bottom)}
        """
        results = []
        if frame is None:
            return results

        small = cv2.resize(frame, (0, 0), fx=self.resize_scale, fy=self.resize_scale)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(rgb_small)
        encodings = face_recognition.face_encodings(rgb_small, locations)

        for (top, right, bottom, left), enc in zip(locations, encodings):
            name = "Unknown"
            if self.known_faces:
                dists = face_recognition.face_distance(self.known_faces, enc)
                best_idx = np.argmin(dists)
                if dists[best_idx] < self.distance_threshold:
                    name = self.known_face_names[best_idx]

            # scale back to original frame size
            scale = 1.0 / self.resize_scale
            l = int(left * scale)
            t = int(top * scale)
            r = int(right * scale)
            b = int(bottom * scale)
            results.append({'name': name, 'bbox': (l, t, r, b)})
        return results
