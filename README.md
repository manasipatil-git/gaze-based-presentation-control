# FocusLock

> **Hardware-free webcam-based gaze-controlled presentation system.**

FocusLock is an educational computer-vision project that transforms a standard laptop webcam into a hands-free gaze-driven controller for slide presentations.

---

## 📌 Architecture Pipeline

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

## 🚀 MVP Implementation Status

- [x] **Stage 1 — Sensing & Iris Extraction:** MediaPipe Tasks API with 478-landmark mesh & iris centroids.
- [x] **Stage 2 — Gaze Normalization & Filtering:** Dual-eye socket relative ratio & sliding-window moving-average filter.
- [x] **Stage 3 — 5-Point Calibration:** Interactive 5-target linear least-squares screen mapping (`calibration.json`).
- [x] **Stage 4 — Dwell-Based Intent Detection:** 1.8s dwell state machine solving the *"Midas Touch"* problem.
- [x] **Stage 5 — Presentation Control:** PyAutoGUI slide-advance keyboard binding with safe `DEMO_MODE` toggle.
- [x] **Stage 6 — Telemetry Logging & Benchmarking:** Frame telemetry logger & 3-panel matplotlib analysis script.

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

3. **Run FocusLock:**
   ```bash
   python main.py
   ```

---

## 🎮 Live Keyboard Controls

| Key | Action | Description |
|:---:|:---:|---|
| **`d`** | **Toggle Demo / Live Mode** | Switches between safe simulation (printing only) and live OS keypresses. |
| **`l`** | **Toggle Telemetry Logging** | Starts or pauses frame-by-frame telemetry recording to `data/logs/gaze_log.csv`. |
| **`c`** | **Run 5-Point Calibration** | Starts the interactive calibration target sequence (Top-L $\to$ Top-R $\to$ Center $\to$ Bottom-L $\to$ Bottom-R). |
| **`r`** | **Reset Calibration** | Clears active calibration and dwell states. |
| **`q`** / **`ESC`** | **Quit & Save** | Safely flushes telemetry logs, releases camera, and exits. |

---

## 📊 Generating Scientific Benchmark Graphs

After running FocusLock, analyze your real eye telemetry:

```bash
python plot_benchmarks.py
```

This generates a 3-panel figure saved at **`data/logs/gaze_benchmark.png`**:
1. **Jitter Reduction:** Overlays raw sensor gaze vs. moving-average smoothed gaze over time.
2. **Intent & Trigger Events:** Plots calibrated screen coordinates with Left/Right trigger zones and timestamps of slide commands.
3. **2D Trajectory:** Plots raw 2D spatial scatter against the smoothed eye-path.

*(No synthetic or fabricated benchmark numbers are used—only real empirical data from testing).*

---

## ⚠️ Current MVP Limitations (Honest Academic Assessment)

- **Webcam-based gaze estimation is approximate:** Standard RGB webcams lack depth sensors and infrared illumination.
- **Lighting sensitivity:** Drastic shifts in room lighting or backlighting alter eyelid boundary segmentation.
- **Head rotation drift:** Severe head tilting alters the eye reference frame (future work will add full 3D head-pose compensation).
- **First-order linear mapping:** Approximates spherical eye rotations using planar 1D linear regression.
- **Kalman filtering:** The moving-average filter successfully removes high-frequency jitter; full state-space Kalman filtering is planned for the next development phase.
- **Intent thresholding:** Dwell-based intent is effective for presentation navigation, but multi-user statistical validation remains future work.

---

## 📄 Complete Project Documentation

- 📘 [`FocusLock_Guidebook.pdf`](FocusLock_Guidebook.pdf) — Complete engineering architecture, mathematical formulas, and viva defense guide.
- 📋 [`FocusLock_Progress_Report.pdf`](FocusLock_Progress_Report.pdf) — Formal progress report prepared for faculty advisors.
