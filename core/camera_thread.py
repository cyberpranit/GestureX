import os
import cv2
import time
import logging
import urllib.request
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

logger = logging.getLogger("GestureX.Camera")

HAND_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
FACE_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

class CameraThread(QThread):
    # Signals
    frame_ready = pyqtSignal(QImage)
    hands_detected = pyqtSignal(list, tuple)
    face_detected = pyqtSignal(list, np.ndarray, tuple) # Face landmarks + raw frame + frame size
    status_message = pyqtSignal(str)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.running = False
        self.cap = None

    def _get_or_download_models(self):
        core_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.status_message.emit("Checking model files...")
        hand_path = os.path.join(core_dir, "hand_landmarker.task")
        if not os.path.exists(hand_path):
            self.status_message.emit("Downloading hand model (7MB)...")
            logger.info(f"Downloading hand landmark model to: {hand_path}")
            urllib.request.urlretrieve(HAND_MODEL_URL, hand_path)
            
        face_path = os.path.join(core_dir, "face_landmarker.task")
        if not os.path.exists(face_path):
            self.status_message.emit("Downloading face model (5MB)...")
            logger.info(f"Downloading face landmark model to: {face_path}")
            urllib.request.urlretrieve(FACE_MODEL_URL, face_path)
            
        return hand_path, face_path

    def run(self):
        self.running = True
        
        try:
            hand_model, face_model = self._get_or_download_models()
        except Exception as e:
            logger.critical(f"Failed to prepare MediaPipe task models: {e}")
            self.status_message.emit("Failed to download model files.")
            self.running = False
            return

        # Initialize MediaPipe Tasks
        try:
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            # Setup Hands
            hands_base_options = python.BaseOptions(model_asset_path=hand_model)
            hands_options = vision.HandLandmarkerOptions(
                base_options=hands_base_options,
                running_mode=vision.RunningMode.IMAGE,
                num_hands=2
            )
            hands_detector = vision.HandLandmarker.create_from_options(hands_options)
            
            # Setup Face
            face_base_options = python.BaseOptions(model_asset_path=face_model)
            face_options = vision.FaceLandmarkerOptions(
                base_options=face_base_options,
                running_mode=vision.RunningMode.IMAGE,
                num_faces=1
            )
            face_detector = vision.FaceLandmarker.create_from_options(face_options)
        except Exception as e:
            logger.critical(f"Failed to initialize MediaPipe Tasks detectors: {e}")
            self.status_message.emit("Detector initialization failed.")
            self.running = False
            return

        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            self.status_message.emit(f"Webcam index {self.camera_index} could not be opened.")
            self.running = False
            return

        logger.info(f"Started camera processing thread using index: {self.camera_index}")
        self.status_message.emit("Camera Active")

        # Core loop
        while self.running:
            start_time = time.time()
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to grab camera frame. Retrying...")
                time.sleep(0.1)
                continue

            # Mirror frame for natural interaction
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape

            # Convert to RGB for MediaPipe Tasks
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detect Hands
            hands_data = []
            try:
                hands_results = hands_detector.detect(mp_image)
                if hands_results and hands_results.hand_landmarks:
                    for idx, hand_lms in enumerate(hands_results.hand_landmarks):
                        # Determine handedness label
                        handedness_label = "Right"
                        if idx < len(hands_results.handedness):
                            # category_name is Left or Right
                            raw_label = hands_results.handedness[idx][0].category_name
                            # Flip because self-view camera is mirrored
                            handedness_label = "Left" if raw_label == "Right" else "Right"
                        
                        # Pack coordinates as (x, y, z) list compatible with existing modules
                        lms = [(lm.x, lm.y, lm.z) for lm in hand_lms]
                        
                        hands_data.append({
                            "landmarks": lms,
                            "handedness": handedness_label
                        })

                        # Draw skeletal connections in OpenCV
                        self._draw_hand_skeleton(frame, lms)
            except Exception as hands_err:
                logger.error(f"Error during hand detection: {hands_err}")

            # Emit hand events
            self.hands_detected.emit(hands_data, (w, h))

            # Detect Face
            try:
                face_results = face_detector.detect(mp_image)
                if face_results and face_results.face_landmarks:
                    face_lms = face_results.face_landmarks[0]
                    face_list = [(lm.x, lm.y, lm.z) for lm in face_lms]
                    
                    self.face_detected.emit(face_list, frame.copy(), (w, h))
                    
                    # Draw key facial dots
                    for pt_idx in [33, 263, 10, 152]: # Left Eye, Right Eye, Forehead, Chin
                        pt = face_lms[pt_idx]
                        cx, cy = int(pt.x * w), int(pt.y * h)
                        cv2.circle(frame, (cx, cy), 3, (255, 0, 127), -1)
            except Exception as face_err:
                logger.error(f"Error during face detection: {face_err}")

            # Convert frame back to RGB and stream to PyQt QLabel
            cv_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = 3 * w
            q_img = QImage(cv_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.frame_ready.emit(q_img.copy())

            # Regulate FPS (target 30 FPS -> ~33ms interval)
            elapsed = time.time() - start_time
            sleep_time = max(0.01, 0.033 - elapsed)
            time.sleep(sleep_time)

        # Cleanup
        if self.cap:
            self.cap.release()
        hands_detector.close()
        face_detector.close()
        logger.info("Camera thread stopped.")

    def _draw_hand_skeleton(self, frame, landmarks):
        h, w, c = frame.shape
        connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index
            (5, 6), (6, 7), (7, 8),
            # Middle
            (9, 10), (10, 11), (11, 12),
            # Ring
            (13, 14), (14, 15), (15, 16),
            # Pinky
            (17, 18), (18, 19), (19, 20),
            # Palm Connections
            (0, 5), (5, 9), (9, 13), (13, 17), (17, 0)
        ]
        
        # Draw connections (electric blue)
        for start, end in connections:
            pt1 = landmarks[start]
            pt2 = landmarks[end]
            cx1, cy1 = int(pt1[0] * w), int(pt1[1] * h)
            cx2, cy2 = int(pt2[0] * w), int(pt2[1] * h)
            cv2.line(frame, (cx1, cy1), (cx2, cy2), (255, 210, 0), 2)
            
        # Draw joints (neon green)
        for lm in landmarks:
            cx, cy = int(lm[0] * w), int(lm[1] * h)
            cv2.circle(frame, (cx, cy), 3, (65, 255, 0), -1)

    def stop(self):
        self.running = False
        self.wait()
