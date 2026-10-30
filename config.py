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
DETECTION_CONFIDENCE  = 0.6    # Min confidence to detect a face
TRACKING_CONFIDENCE   = 0.6    # Min confidence to keep tracking between frames
REFINE_LANDMARKS      = True   # Enables the 10 iris landmarks

# ── Gaze / Filtering ─────────────────────────────────────────────────────────
SMOOTHING_WINDOW = 6      # Rolling history window (frames) for median calculation

# ── Calibration ──────────────────────────────────────────────────────────────
CALIBRATION_FILE    = "calibration.json"
CALIBRATION_SAMPLES = 25   # Frames collected per calibration point (~0.8s per target)

# ── Dwell detection (Tuned for effortless split-screen presentation control) ───
DWELL_TIME          = 1.1    # Seconds gaze must stay inside a zone (1.1s is fast & fatigue-free)
ZONE_WIDTH_FRAC     = 0.25   # 25% of screen width on each edge (easy to reach without head tilt)
DWELL_GRACE_PERIOD  = 0.35   # Seconds of grace tolerance: blinks or brief glances don't reset timer

# ── Presentation control ──────────────────────────────────────────────────────
DEMO_MODE = True   # True → print trigger message; False → send real keypress

# ── Data logging ──────────────────────────────────────────────────────────────
LOG_DIR  = "data/logs"
LOG_FILE = "gaze_log.csv"

# ── Display ───────────────────────────────────────────────────────────────────
WINDOW_NAME = "FocusLock"
