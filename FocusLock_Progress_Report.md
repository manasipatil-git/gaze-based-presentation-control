# PROJECT PROGRESS REPORT: FOCUSLOCK
**A Hardware-Free Webcam-Based Gaze-Control System**  
*Submitted to: Project Incharge / Faculty Advisor*  
*Project Domain: Computer Vision, Human-Computer Interaction, Signal Processing*  
*Current Status: Stages 1, 2, 3 Complete & Verified (Working MVP Prototype)*

---

## 1. Project Objective & Methodology

The goal of **FocusLock** is to create a low-cost, hands-free slide navigation system using an ordinary laptop webcam, eliminating the need for expensive dedicated infrared eye-tracking hardware.

### Core Engineering Principle
> **MediaPipe is used exclusively as a raw geometric sensor.**  
> The core algorithmic contributions of this project are the subsequent stages developed from scratch: **Spatial Normalization**, **Sliding-Window Jitter Filtering**, **5-Point Linear Calibration Regression**, and **Dwell-Based Intent Recognition**.

---

## 2. Implementation Status Summary

| Stage | Module Name | Status | Deliverable Accomplished |
|---|---|---|---|
| **Stage 1** | Sensing & Iris Extraction | **COMPLETED** | MediaPipe 478-landmark tracking, iris centroid extraction (Landmarks 468 & 473). |
| **Stage 2** | Gaze Normalization & Filter | **COMPLETED** | Bounding-box ratio normalization, dual-eye fusion, sliding-window moving-average filter ($N=7$). |
| **Stage 3** | 5-Point Screen Calibration | **COMPLETED** | Interactive 5-target routine, 1D least-squares polynomial fit (`numpy.polyfit`), JSON caching. |
| **Stage 4** | Dwell Intent Detection | **IN PROGRESS** | Continuous 1.8s dwell timer state machine to eliminate the *"Midas Touch"* error. |
| **Stage 5** | Presentation Controller | **NEXT PHASE** | PyAutoGUI slide-advance keyboard binding with safe `DEMO_MODE` toggle. |
| **Stage 6** | Telemetry Logging & Plots | **NEXT PHASE** | CSV real-time coordinate logger for empirical latency & precision graphs. |

---

## 3. Detailed Work Completed So Far (Stages 1 – 3)

### Stage 1: MediaPipe Iris & Landmark Extraction (`tracking/iris_tracker.py`)
- **Modern MediaPipe Tasks Integration:** Configured `FaceLandmarker` with the standalone 478-point `face_landmarker.task` model bundle, ensuring compatibility with modern Python environments.
- **Iris Coordinates:** Extracted pixel centroids for the right iris (Index 468) and left iris (Index 473).
- **Live Visual Feedback:** Implemented a real-time OpenCV HUD rendering live FPS (~30 FPS on CPU), face detection state, and pupil indicators.

### Stage 2: Gaze Normalization & Moving-Average Filter (`tracking/gaze_estimator.py`, `filtering/moving_average.py`)
- **Mathematical Normalization:** Formulated dimensionless ratios within the eye bounding box:
  $$\text{Gaze}_X = \frac{\text{Iris}_X - X_{\min}}{X_{\max} - X_{\min}}, \quad \text{Gaze}_Y = \frac{\text{Iris}_Y - Y_{\min}}{Y_{\max} - Y_{\min}}$$
  This makes iris measurements invariant to minor head movements and distance from the camera.
- **Dual-Eye Fusion:** Averaged left and right eye vectors to mitigate unilateral eyelid occlusion.
- **Jitter Reduction Filter:** Implemented a FIFO sliding-window moving-average filter ($N=7$). This eliminates optical noise and involuntary microsaccadic tremor with minimal latency (~230ms).
- **Visual Gaze Radar:** Created a real-time 2D radar HUD visually comparing **RAW (Red)** vs **FILTERED (Green)** gaze trajectories.

### Stage 3: 5-Point Calibration & Screen Coordinate Mapping (`calibration/calibrator.py`, `ui/overlay.py`)
- **Why Calibration is Essential:** Physical eye rotation across a laptop screen only spans a narrow band ($0.35$ to $0.65$) in normalized space. Calibration amplifies and shifts this range to span the full screen $[0.0, 1.0]$.
- **5-Target Routine:** Developed an interactive calibration state machine (Top-Left, Top-Right, Center, Bottom-Left, Bottom-Right), collecting 30 sample frames per point.
- **Linear Least-Squares Regression:** Fitted optimal gain ($m$) and offset ($c$) per axis using `numpy.polyfit`:
  $$X_{\text{screen}} = m_x \cdot G_x + c_x, \quad Y_{\text{screen}} = m_y \cdot G_y + c_y$$
- **Persistence:** Saved calibration parameters in `calibration.json` for automatic loading across restarts.
- **Trigger Zone Overlay:** Rendered calibrated crosshairs and defined left ($0\text{–}15\%$) and right ($85\text{–}100\%$) trigger zones on the live viewport.

---

## 4. Key Engineering Problem Solved
- **Challenge:** Deprecation of the legacy `mediapipe.solutions` module in Python 3.13 / MediaPipe 0.10.x caused runtime import errors.
- **Solution:** Re-engineered the tracking layer to interface directly with the **MediaPipe Tasks Python API** (`mediapipe.tasks.python.vision.FaceLandmarker`), automating model asset caching and landmark rendering.

---

## 5. Next Immediate Steps (To Complete MVP)
1. **Stage 4 (Dwell Intent Detection):** Complete continuous timer thresholding ($1.8\text{s}$) when gaze enters trigger zones to prevent accidental activations.
2. **Stage 5 (Presentation Actuation):** Integrate `pyautogui.press('right')` / `pyautogui.press('left')` with a safe `DEMO_MODE` toggle.
3. **Stage 6 (Telemetry Logging & Benchmark Report):** Log real-time frame telemetry to CSV and generate quantitative accuracy/jitter plots.
