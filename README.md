# FocusLock

> **Hardware-free webcam-based gaze-controlled presentation system.**

FocusLock is an educational computer-vision project that turns a standard laptop webcam into a hands-free gaze-driven controller for slide presentations.

---

## 📌 Architecture Overview

```
Webcam (BGR)
    │
    ▼
MediaPipe Tasks FaceLandmarker (Iris Centroids 468 & 473)
    │
    ▼
Dual-Eye Gaze Normalization (Eye Bounding Box ratio)
    │
    ▼
Temporal Jitter Reduction (Moving Average Filter, N=7)
    │
    ▼
5-Point Screen Calibration (1D Linear Regression via numpy.polyfit)
    │
    ▼
Dwell-Based Intent Detection (1.8s Threshold)
    │
    ▼
Presentation Actuation (PyAutoGUI Left/Right Arrow Dispatch)
```

---

## 🚀 Current MVP Status

- [x] **Stage 1 — Sensing & Iris Extraction:** MediaPipe Tasks API integration with 478-landmark mesh & iris centroids.
- [x] **Stage 2 — Gaze Normalization & Filtering:** Dual-eye socket relative ratio & sliding-window moving-average filter.
- [x] **Stage 3 — 5-Point Calibration:** Interactive 5-target linear least-squares screen mapping (`calibration.json`).
- [ ] **Stage 4 — Dwell Intent Detection:** Continuous gaze timer to prevent the *Midas Touch* problem.
- [ ] **Stage 5 — Presentation Control:** PyAutoGUI keyboard binding with `DEMO_MODE` safety switch.
- [ ] **Stage 6 — CSV Data Logging & Benchmark:** Telemetry export and accuracy plots.

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/manasipatil-git/gaze-based-presentation-control.git
   cd gaze-based-presentation-control
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

---

## 🎮 Controls

| Key | Action |
|---|---|
| **`c`** | Start / Re-run interactive 5-Point Calibration |
| **`r`** | Reset calibration |
| **`q`** or **`ESC`** | Quit application |

---

## 📊 Calibration Procedure

1. Launch `python main.py` and press **`c`**.
2. Fix your gaze on the 5 target points as they appear:
   - **Top-Left** $\to$ **Top-Right** $\to$ **Center** $\to$ **Bottom-Left** $\to$ **Bottom-Right**
3. Once calibration completes, the calibrated gaze crosshair will track your point of regard on screen.

---

## ⚠️ Current Limitations (Honest MVP Assessment)

- **Webcam-based gaze estimation is approximate:** Standard RGB webcams lack depth sensors and infrared illumination.
- **Lighting variations:** Drastic shifts in ambient lighting alter eyelid boundary segmentation.
- **Head movement:** Large head rotations can cause calibration drift (future versions will incorporate full 3D head-pose compensation).
- **First-order linear mapping:** Approximates spherical eye rotations using planar 1D linear equations.
- **Kalman filtering:** Moving-average filter is implemented; Kalman filter is reserved for next development iteration.

---

## 📄 Documentation & Reports

- 📘 [`FocusLock_Guidebook.pdf`](FocusLock_Guidebook.pdf) — Complete technical reference and viva preparation guide.
- 📋 [`FocusLock_Progress_Report.pdf`](FocusLock_Progress_Report.pdf) — Formal progress report for faculty advisors.
