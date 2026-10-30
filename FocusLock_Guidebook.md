# FocusLock: Engineering & Architecture Guidebook
**Hardware-Free Webcam-Based Gaze-Control System (Full MVP Delivered)**  
*Complete 6-Stage Architecture, Mathematical Formulations, Code Modules, and Viva Preparation Guide*

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
[ Stage 1: Sensing Layer ]             ──► MediaPipe Tasks FaceLandmarker (Iris Centroids 468 & 473)
         │
         ▼
[ Stage 2: Spatial Normalization ]     ──► Scale-invariant eye-socket ratio [0.0, 1.0]
         │
         ▼
[ Stage 2: Temporal Filtering ]        ──► Moving-Average Filter (N=7 sliding window jitter reduction)
         │
         ▼
[ Stage 3: Calibration Layer ]         ──► 5-Point linear least-squares regression (numpy.polyfit)
         │
         ▼
[ Stage 4: Intent Detection ]          ──► Continuous 1.8s dwell timer with single-shot lock
         │
         ▼
[ Stage 5: Physical Actuation ]        ──► PyAutoGUI keyboard controller (Left/Right arrows with DEMO_MODE)
         │
         ▼
[ Stage 6: Telemetry & Evaluation ]    ──► Frame-by-frame CSV telemetry logging & benchmark graphing
```

---

## 2. Full Architecture Pipeline & Modules

| Stage | Module Name | Primary Function | Key Algorithm / Math |
|:---:|---|---|---|
| **1. Sensing** | `tracking/iris_tracker.py` | Extracts 478 face & iris landmarks from BGR frames | MediaPipe Tasks `FaceLandmarker` |
| **2. Normalization** | `tracking/gaze_estimator.py` | Maps iris coordinates relative to eyelid boundaries | Ratio: $(\text{Iris} - \min) / (\max - \min)$ |
| **2. Filtering** | `filtering/moving_average.py` | Eliminates optical tremor & microsaccades | Sliding FIFO Mean ($N=7$ frames) |
| **3. Calibration** | `calibration/calibrator.py` | Maps physiological eye span to screen bounds $[0.0, 1.0]$ | 1D Linear Regression (`numpy.polyfit`) |
| **4. Intent** | `intent/dwell_detector.py` | Distinguishes deliberate gaze from glances | Continuous dwell timer ($1.8\text{s}$) with lock |
| **5. Actuation** | `control/presentation_controller.py` | Dispatches OS-level slide advance keypresses | PyAutoGUI with `DEMO_MODE` safety switch |
| **6. Telemetry** | `data/logger.py` & `plot_benchmarks.py` | Frame telemetry recording & scientific plotting | Pandas CSV logging & Matplotlib figures |

---

## 3. Mathematical & Algorithmic Formulations

### A. Spatial Eye-Socket Normalization
$$\text{Eye Width} = X_{\max} - X_{\min}, \quad \text{Eye Height} = Y_{\max} - Y_{\min}$$
$$\text{Gaze}_X = \frac{\text{Iris}_X - X_{\min}}{\text{Eye Width}}, \quad \text{Gaze}_Y = \frac{\text{Iris}_Y - Y_{\min}}{\text{Eye Height}}$$
*Dual-Eye Fusion:*
$$\text{Gaze}_{\text{fused}} = \frac{\text{Gaze}_{\text{left}} + \text{Gaze}_{\text{right}}}{2.0}$$

### B. Moving-Average Jitter Reduction
$$\text{Filtered}(t) = \frac{1}{N} \sum_{i=0}^{N-1} \text{Raw}(t - i) \quad (N=7)$$
Eliminates high-frequency sensor noise while keeping perceptual latency below $\approx 230\text{ms}$.

### C. 1D Least-Squares Calibration Mapping
$$X_{\text{screen}} = m_x \cdot G_x + c_x, \quad Y_{\text{screen}} = m_y \cdot G_y + c_y$$
Where $m$ represents Gain (amplification) and $c$ represents Offset (centering bias).

### D. Dwell-Based Intent State Machine
A timer starts upon entry into the Left ($0\text{--}15\%$) or Right ($85\text{--}100\%$) trigger zone. Once $\Delta t \ge 1.8\text{s}$, a single-shot event is dispatched and locked until the user returns their gaze toward center, solving the *"Midas Touch"* problem.

---

## 4. Evaluator & Viva Defense Q&A Cheatsheet

| Evaluator Question | Strong Technical Answer |
|---|---|
| **Why not train an end-to-end Deep Learning model?** | Deep learning models for direct gaze are black boxes requiring vast GPU power and thousands of labeled user gaze images. Our modular pipeline runs in real-time on standard CPUs (30+ FPS) and provides clear geometric interpretability. |
| **What is the 'Midas Touch' problem?** | The human eye is primarily a perceptive organ. Everywhere you look cannot trigger an action. Dwell-time intent detection ensures only deliberate, sustained focus initiates a command. |
| **Why does webcam gaze need calibration?** | Across a computer monitor, human irises physically traverse only a narrow subsection of the eye socket ($0.35$ to $0.65$). Without calibration, screen edges are unreachable. |
| **What causes calibration drift?** | 1. Severe head rotation changing camera perspective.<br>2. Lighting variations altering eyelid thresholding.<br>3. Planar approximation error from fitting linear 1D equations to spherical eye rotations. |
