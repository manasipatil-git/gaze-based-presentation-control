# FocusLock: Complete Technical Guidebook
**Hardware-Free Webcam-Based Gaze-Control System (MVP)**  
*Step-by-Step Architecture, Mathematical Formulations, and Demonstration Guide*

---

## 1. Executive Summary & Core Philosophy

**FocusLock** is an educational computer vision project that transforms an ordinary webcam into a hands-free gaze-driven controller for slide presentations.

### The Core College Demo Philosophy
> **"MediaPipe is only the sensor; our pipeline is the project."**

Commercial eye-trackers use expensive infrared illuminators and high-speed IR cameras. FocusLock uses standard RGB imagery. The core engineering contribution is how we process noisy optical landmarks through a structured multi-stage pipeline:

```
[ Webcam BGR Frame ]
         │
         ▼
[ Stage 1: MediaPipe Tasks FaceLandmarker ] ──► 478 3D Landmarks (Iris 468, 473)
         │
         ▼
[ Stage 2: Dual-Eye Normalization ]        ──► Dimensionless Ratio [0.0, 1.0]
         │
         ▼
[ Stage 2: Moving-Average Filter ]         ──► High-frequency Jitter Removal (N=7)
         │
         ▼
[ Stage 3: 5-Point Least-Squares Calibrator] ─► Screen Coordinate Mapping [0.0, 1.0]
         │
         ▼
[ Stage 4: Dwell-Time Intent Detector ]     ──► Solves the "Midas Touch" Problem (1.8s)
         │
         ▼
[ Stage 5: PyAutoGUI Keyboard Controller ]  ──► Emits Left / Right Arrow Key Events
         │
         ▼
[ Stage 6: CSV Data Logging & Evaluation ]  ──► Empirical Benchmarking
```

---

## 2. Stage-by-Stage Detailed Breakdown

### Stage 1: Sensing & Iris Extraction (`tracking/iris_tracker.py`)

* **What happened:**  
  Configured MediaPipe's modern `FaceLandmarker` Tasks API with the 478-landmark bundle `face_landmarker.task`.
* **Key Landmarks Used:**
  * Landmark **468**: Anatomical Right Iris Center
  * Landmark **473**: Anatomical Left Iris Center
  * Eye Contour Indices: Eyelid oval boundaries used to calculate eye bounding boxes
* **Key Implementation Details:**
  * **Color Conversion:** OpenCV decodes in **BGR**; MediaPipe requires **RGB** (`cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)`).
  * **Mirror Mode:** `cv2.flip(frame, 1)` mirrors horizontal video so user movements feel intuitive.

---

### Stage 2: Dual-Eye Normalization & Signal Smoothing (`tracking/gaze_estimator.py`, `filtering/moving_average.py`)

* **What happened:**  
  Converted raw pixel coordinates to scale-invariant socket-relative values and filtered sensor noise.
* **Normalization Formula:**
  $$\text{Eye Width} = X_{\max} - X_{\min}, \quad \text{Eye Height} = Y_{\max} - Y_{\min}$$
  $$\text{Gaze}_X = \frac{\text{Iris}_X - X_{\min}}{\text{Eye Width}}, \quad \text{Gaze}_Y = \frac{\text{Iris}_Y - Y_{\min}}{\text{Eye Height}}$$
  *Why this matters:* When your head moves, both the eyelid boundaries and the iris shift together, making the ratio partially head-pose invariant.
* **Dual-Eye Fusion:**
  $$\text{Gaze}_{\text{fused}} = \frac{\text{Gaze}_{\text{left}} + \text{Gaze}_{\text{right}}}{2.0}$$
* **Moving Average Filter:**
  $$\text{Filtered}(t) = \frac{1}{N} \sum_{i=0}^{N-1} \text{Raw}(t - i)$$
  *Trade-off:* $N=7$ window at 30 FPS introduces $\approx 230\text{ms}$ delay while eliminating high-frequency tremor and micro-saccades.

---

### Stage 3: 5-Point Calibration & Screen Mapping (`calibration/calibrator.py`)

* **What happened:**  
  Created an interactive calibration procedure mapping physiological eye movement into screen space.
* **Why Calibration is Mandatory:**  
  When looking across a monitor, human irises physically travel only a narrow subsection of the eye socket (typically between $0.35$ and $0.65$). Without calibration, screen corners are unreachable.
* **5 Target Calibration Points:**
  1. Top-Left: `(0.15, 0.15)`
  2. Top-Right: `(0.85, 0.15)`
  3. Center: `(0.50, 0.50)`
  4. Bottom-Left: `(0.15, 0.85)`
  5. Bottom-Right: `(0.85, 0.85)`
* **Linear Regression Model (`numpy.polyfit`):**
  $$X_{\text{screen}} = m_x \cdot G_x + c_x$$
  $$Y_{\text{screen}} = m_y \cdot G_y + c_y$$
  *Where $m$ is the Gain (amplification) and $c$ is the Offset (center bias).*
* **Persistence:** Saved in `calibration.json` to avoid re-calibrating across sessions.

---

## 3. Road Ahead (Stages 4, 5, 6 Preview)

* **Stage 4 (Dwell Intent Detection):** Requires continuous gaze in Left ($0\text{–}15\%$) or Right ($85\text{–}100\%$) trigger zones for $1.8\text{s}$ to prevent accidental slide changes.
* **Stage 5 (PyAutoGUI Controller):** Translates confirmed intent into real Left/Right arrow key strokes, protected by `DEMO_MODE`.
* **Stage 6 (CSV Logging & Evaluation):** Dumps real $(X, Y)$ timestamps and states for quantitative graphing and accuracy reports.

---

## 4. Evaluator & Viva Defense Q&A Cheatsheet

| Evaluator Question | Strong Technical Answer |
|---|---|
| **Why not train an end-to-end Deep Learning model?** | Deep learning models for direct gaze are black boxes requiring vast GPU power and thousands of labeled user gaze images. Our modular pipeline runs in real-time on standard CPUs (30+ FPS) and provides clear geometric interpretability. |
| **What is the 'Midas Touch' problem?** | The human eye is primarily a perceptive organ. Everywhere you look cannot trigger an action. Dwell-time intent detection ensures only deliberate, sustained focus initiates a command. |
| **What causes calibration drift?** | 1. Severe head translation/rotation changing the camera angle.<br>2. Changes in ambient lighting altering eyelid thresholding.<br>3. Planar approximation error from fitting linear 1D equations to spherical eye rotations. |
