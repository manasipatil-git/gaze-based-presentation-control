# config.py
# ─────────────────────────────────────────────────────────────────────────────
# Central configuration for FocusLock.
# All tunable constants live here so you never need to hunt through other files.
# ─────────────────────────────────────────────────────────────────────────────

# ── Webcam ────────────────────────────────────────────────────────────────────
CAMERA_INDEX = 0          # 0 = default webcam; change if you have multiple cameras
FRAME_WIDTH  = 1280       # Requested capture width  (camera may override)
FRAME_HEIGHT = 720        # Requested capture height

# ── MediaPipe FaceMesh ────────────────────────────────────────────────────────
MAX_FACES             = 1      # We only need one face
DETECTION_CONFIDENCE  = 0.7    # Min confidence to detect a face
TRACKING_CONFIDENCE   = 0.7    # Min confidence to keep tracking between frames
REFINE_LANDMARKS      = True   # MUST be True — this enables the iris landmarks

# ── Gaze / Filtering ─────────────────────────────────────────────────────────
SMOOTHING_WINDOW = 7      # Moving-average window size (frames)

# ── Calibration ──────────────────────────────────────────────────────────────
CALIBRATION_FILE    = "calibration.json"
CALIBRATION_SAMPLES = 30   # Frames collected per calibration point

# ── Dwell detection ───────────────────────────────────────────────────────────
DWELL_TIME      = 1.8      # Seconds the gaze must stay inside a zone to trigger
ZONE_WIDTH_FRAC = 0.15     # Zone occupies this fraction of screen width on each edge

# ── Presentation control ──────────────────────────────────────────────────────
DEMO_MODE = True   # True → print trigger message; False → send real keypress

# ── Data logging ──────────────────────────────────────────────────────────────
LOG_DIR  = "data/logs"
LOG_FILE = "gaze_log.csv"

# ── Display ───────────────────────────────────────────────────────────────────
WINDOW_NAME = "FocusLock"
