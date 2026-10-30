# PROJECT PROGRESS REPORT: FOCUSLOCK
**A Hardware-Free Webcam-Based Gaze-Control System (Full MVP Delivered)**  
*Submitted to: Project Incharge / Faculty Advisor*  
*Project Domain: Computer Vision, Human-Computer Interaction, Signal Processing*  
*Delivery Phase: Working MVP (All 6 Stages Completed & Verified)*

---

## 1. Project Objective & Methodology

The goal of **FocusLock** is to develop a contact-free, low-cost slide navigation system using an ordinary laptop webcam, eliminating the need for expensive dedicated infrared eye-tracking hardware.

### Core Engineering Principle
> **MediaPipe is used exclusively as a raw geometric sensor.**  
> The core algorithmic contributions of this project are the subsequent stages developed from scratch: **Spatial Normalization**, **Sliding-Window Jitter Filtering**, **5-Point Linear Calibration Regression**, **Dwell-Based Intent Recognition**, **OS Actuation Integration**, and **Empirical Telemetry Benchmarking**.

---

## 2. Implementation Status Summary (All 6 Stages Completed)

| Stage | Module Name | Status | Deliverable Accomplished |
|:---:|---|:---:|---|
| **Stage 1** | Sensing & Iris Extraction | **COMPLETED** | MediaPipe 478-landmark tracking, iris centroid extraction (Landmarks 468 & 473). |
| **Stage 2** | Gaze Normalization & Filter | **COMPLETED** | Bounding-box ratio normalization, dual-eye fusion, sliding-window moving-average filter ($N=7$). |
| **Stage 3** | 5-Point Screen Calibration | **COMPLETED** | Interactive 5-target routine, 1D least-squares polynomial fit (`numpy.polyfit`), JSON caching. |
| **Stage 4** | Dwell Intent Detection | **COMPLETED** | Continuous 1.8s dwell timer state machine eliminating the *"Midas Touch"* error. |
| **Stage 5** | Presentation Controller | **COMPLETED** | PyAutoGUI slide-advance keyboard binding with safe `DEMO_MODE` toggle (`'d'`). |
| **Stage 6** | Telemetry Logging & Plots | **COMPLETED** | Real-time CSV logging (`data/logs/gaze_log.csv`) & 3-panel matplotlib benchmark analysis script. |

---

## 3. Detailed Pipeline Architecture & Results

### Stage 1: MediaPipe Iris & Landmark Extraction (`tracking/iris_tracker.py`)
- Configured MediaPipe Tasks `FaceLandmarker` with standalone 478-point model bundle (indices 468 & 473 for pupil centers), achieving 30+ FPS on CPU.

### Stage 2: Gaze Normalization & Moving-Average Filter (`tracking/gaze_estimator.py`, `filtering/moving_average.py`)
- Implemented scale-invariant eye-socket boundary ratios: $\text{Gaze} = (\text{Iris} - \text{Eye}_{\min}) / \text{Eye}_{\text{span}}$. Dual-eye fusion averages left and right eye vectors.
- FIFO sliding-window filter ($N=7$) successfully eliminates high-frequency optical sensor tremor and microsaccades.

### Stage 3: 5-Point Calibration & Screen Coordinate Mapping (`calibration/calibrator.py`)
- 5-point target sequence (Top-L, Top-R, Center, Bottom-L, Bottom-Right) maps narrow physiological iris range ($0.35\text{–}0.65$) to screen space $[0.0, 1.0]$ via `numpy.polyfit` linear regression.

### Stage 4: Dwell-Based Intent Detection (`intent/dwell_detector.py`)
- Formulated continuous 1.8s dwell state machine with single-shot lock, solving the classic *"Midas Touch"* false-positive trigger problem.

### Stage 5: Presentation Actuation & Safety Toggle (`control/presentation_controller.py`)
- Dispatches OS keyboard arrow events via PyAutoGUI. Dynamic runtime `DEMO_MODE` switch (`'d'` key) allows safe simulation during testing.

### Stage 6: Telemetry Logging & Benchmark Graphing (`data/logger.py`, `plot_benchmarks.py`)
- Records frame telemetry (timestamp, raw X/Y, filtered X/Y, calibrated X/Y, zone, action) to `data/logs/gaze_log.csv`. Matplotlib script generates 3-panel scientific benchmark charts.

---

## 4. Academic Evaluation & Limitations

**Honest Academic Assessment:**
1. **Hardware Boundaries:** Ordinary webcams lack IR illumination; strong ambient lighting shifts can distort eyelid contour detection.
2. **Head Motion:** Pronounced head rotations introduce coordinate drift, solvable in future work via 3D head-pose homography.
3. **Model Simplicity:** Linear least-squares mapping is computationally lightweight and interpretable, though a polynomial model could better capture spherical eyeball geometry.
