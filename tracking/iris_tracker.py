# tracking/iris_tracker.py
# ─────────────────────────────────────────────────────────────────────────────
# IrisTracker wraps MediaPipe FaceLandmarker (modern MediaPipe Tasks API).
#
# HOW MEDIAPIPE FACELANDMARKER WORKS (important for your demo explanation):
#   MediaPipe FaceLandmarker detects 478 3-D landmarks on a face.
#   It includes:
#     - 468 face mesh landmarks (eyelids, lips, face oval, tessellation)
#     - 10 IRIS landmarks:
#         Index 473: Anatomical Left Iris Center  (surrounded by 474-477)
#         Index 468: Anatomical Right Iris Center (surrounded by 469-472)
#
#   CORRECT ANATOMICAL PAIRING:
#     - Left Eye Contour (indices 362...263) <---> Left Iris Center (473)
#     - Right Eye Contour (indices 33...133) <---> Right Iris Center (468)
#
#   Each landmark provides normalized coordinates (x, y in [0.0, 1.0])
#   relative to image dimensions, and z (depth estimate).
# ─────────────────────────────────────────────────────────────────────────────

import os
import urllib.request
import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import FaceLandmarksConnections

from config import (
    MAX_FACES,
    DETECTION_CONFIDENCE,
    TRACKING_CONFIDENCE,
)

# ── MediaPipe landmark index constants ────────────────────────────────────────
# Correct anatomical pairing:
LEFT_IRIS_CENTER  = 473   # Left iris pupil center (surrounded by 474, 475, 476, 477)
RIGHT_IRIS_CENTER = 468   # Right iris pupil center (surrounded by 469, 470, 471, 472)

# Eye contour indices used for bounding box and normalization
LEFT_EYE_INDICES  = [362, 382, 381, 380, 374, 373, 390, 249,
                     263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE_INDICES = [33,  7,   163, 144, 145, 153, 154, 155,
                     133, 173, 157, 158, 159, 160, 161, 246]

MODEL_PATH = "face_landmarker.task"
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"


class IrisTracker:
    """
    Wraps MediaPipe FaceLandmarker.
    Call process(frame) each frame to get iris centres and eye bounding boxes.
    """

    def __init__(self):
        # Ensure model asset exists locally
        self._ensure_model_exists()

        # Initialize FaceLandmarker using MediaPipe Tasks API
        options = vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=MAX_FACES,
            min_face_detection_confidence=DETECTION_CONFIDENCE,
            min_face_presence_confidence=DETECTION_CONFIDENCE,
            min_tracking_confidence=TRACKING_CONFIDENCE,
            running_mode=vision.RunningMode.IMAGE
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

        self.results       = None
        self.face_detected = False
        self.landmarks     = None

    def _ensure_model_exists(self):
        """Download the official Google MediaPipe face landmarker model if not present."""
        if not os.path.exists(MODEL_PATH):
            print(f"[FocusLock] Downloading {MODEL_PATH} (~30MB)...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("[FocusLock] Model downloaded.")

    # ── Main processing call ─────────────────────────────────────────────────

    def process(self, frame_bgr):
        """
        Run FaceLandmarker on one BGR frame (from OpenCV).
        Returns:
            left_iris_px  – (x, y) pixel coords of left iris centre, or None
            right_iris_px – (x, y) pixel coords of right iris centre, or None
        """
        h, w = frame_bgr.shape[:2]

        # Convert OpenCV BGR -> RGB for MediaPipe Image container
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Run detection
        self.results = self.detector.detect(mp_image)

        if not self.results.face_landmarks or len(self.results.face_landmarks) == 0:
            self.face_detected = False
            self.landmarks     = None
            return None, None

        self.face_detected = True
        self.landmarks = self.results.face_landmarks[0]

        # Convert normalized [0, 1] landmark coordinates to pixel coordinates
        left_iris_px  = self._landmark_to_px(self.landmarks[LEFT_IRIS_CENTER],  w, h)
        right_iris_px = self._landmark_to_px(self.landmarks[RIGHT_IRIS_CENTER], w, h)

        return left_iris_px, right_iris_px

    # ── Helper: landmark → pixel ──────────────────────────────────────────────

    @staticmethod
    def _landmark_to_px(landmark, w, h):
        """Convert a NormalizedLandmark to integer pixel (x, y)."""
        return (int(landmark.x * w), int(landmark.y * h))

    # ── Eye bounding box ─────────────────────────────────────────────────────

    def get_eye_bbox(self, frame_shape, eye="left"):
        """
        Return (x_min, y_min, x_max, y_max) pixel bounding box of one eye.
        Used for gaze normalisation within the eye region.
        """
        if not self.face_detected or self.landmarks is None:
            return None

        h, w = frame_shape[:2]
        indices = LEFT_EYE_INDICES if eye == "left" else RIGHT_EYE_INDICES

        xs = [int(self.landmarks[i].x * w) for i in indices]
        ys = [int(self.landmarks[i].y * h) for i in indices]

        return (min(xs), min(ys), max(xs), max(ys))

    # ── Drawing helpers ───────────────────────────────────────────────────────

    def draw_landmarks(self, frame):
        """
        Draw face tessellation and eye contour lines onto frame.
        """
        if not self.face_detected or self.landmarks is None:
            return

        h, w = frame.shape[:2]

        # Draw eye contours (bright cyan)
        for conn in FaceLandmarksConnections.FACE_LANDMARKS_LEFT_EYE:
            p1 = self._landmark_to_px(self.landmarks[conn.start], w, h)
            p2 = self._landmark_to_px(self.landmarks[conn.end], w, h)
            cv2.line(frame, p1, p2, (255, 255, 0), 1, cv2.LINE_AA)

        for conn in FaceLandmarksConnections.FACE_LANDMARKS_RIGHT_EYE:
            p1 = self._landmark_to_px(self.landmarks[conn.start], w, h)
            p2 = self._landmark_to_px(self.landmarks[conn.end], w, h)
            cv2.line(frame, p1, p2, (255, 255, 0), 1, cv2.LINE_AA)

        # Draw subtle face oval (grey)
        for conn in FaceLandmarksConnections.FACE_LANDMARKS_FACE_OVAL:
            p1 = self._landmark_to_px(self.landmarks[conn.start], w, h)
            p2 = self._landmark_to_px(self.landmarks[conn.end], w, h)
            cv2.line(frame, p1, p2, (180, 180, 180), 1, cv2.LINE_AA)

    def draw_iris(self, frame, left_iris_px, right_iris_px):
        """Draw small circles at each iris centre."""
        if left_iris_px:
            cv2.circle(frame, left_iris_px, 4, (0, 255, 0), -1)   # Green dot
            cv2.circle(frame, left_iris_px, 6, (0, 255, 255), 1)  # Yellow ring
        if right_iris_px:
            cv2.circle(frame, right_iris_px, 4, (0, 255, 0), -1)
            cv2.circle(frame, right_iris_px, 6, (0, 255, 255), 1)

    def close(self):
        """Release MediaPipe resources."""
        self.detector.close()
