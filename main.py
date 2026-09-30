# main.py  — STAGE 3: 5-Point Calibration & Screen Coordinate Mapping
# ─────────────────────────────────────────────────────────────────────────────
# In Stage 3, we introduce:
#   1. Interactive 5-point calibration procedure ('c' key)
#   2. Linear mapping from raw/filtered gaze -> screen coordinates [0.0, 1.0]
#   3. Local persistence in calibration.json
#   4. Live calibrated gaze point visualization with Left/Right trigger zones
#
# Controls:
#   'c' - Start / Re-run 5-point calibration
#   'r' - Reset calibration
#   'q' / ESC - Quit
# ─────────────────────────────────────────────────────────────────────────────

import cv2
import time

from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    SMOOTHING_WINDOW,
    ZONE_WIDTH_FRAC,
    WINDOW_NAME,
)
from tracking.iris_tracker      import IrisTracker
from tracking.gaze_estimator    import GazeEstimator
from filtering.moving_average    import MovingAverageFilter
from calibration.calibrator     import Calibrator
from ui.overlay                 import UIOverlay


def main():
    # ── Open webcam ───────────────────────────────────────────────────────────
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera {CAMERA_INDEX}.")
        return

    print("[FocusLock] Stage 3 — 5-Point Calibration & Coordinate Mapping")
    print("  Press 'c' to start 5-point calibration.")
    print("  Press 'r' to reset calibration.")
    print("  Press 'q' or Escape to quit.")

    # ── Initialize modules ────────────────────────────────────────────────────
    tracker    = IrisTracker()
    estimator  = GazeEstimator()
    filter_    = MovingAverageFilter(window_size=SMOOTHING_WINDOW)
    calibrator = Calibrator()
    ui         = UIOverlay()

    prev_time = time.time()

    # ── Main loop ─────────────────────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame.")
            break

        # Mirror the frame horizontally so eye motion matches intuition
        frame = cv2.flip(frame, 1)

        # ── 1. Detect face and irises ─────────────────────────────────────────
        left_iris_px, right_iris_px = tracker.process(frame)

        left_eye_bbox  = tracker.get_eye_bbox(frame.shape, eye="left")
        right_eye_bbox = tracker.get_eye_bbox(frame.shape, eye="right")

        # ── 2. Calculate normalized gaze ──────────────────────────────────────
        raw_gaze_x, raw_gaze_y = estimator.estimate(
            left_iris_px, left_eye_bbox,
            right_iris_px, right_eye_bbox
        )
        raw_gaze = (raw_gaze_x, raw_gaze_y) if raw_gaze_x is not None else None

        # ── 3. Smooth with Moving-Average Filter ───────────────────────────────
        if raw_gaze is not None:
            filtered_gaze = filter_.update(raw_gaze)
        else:
            filter_.reset()
            filtered_gaze = None

        # ── 4. Calibration state machine ──────────────────────────────────────
        calib_status = calibrator.update_calibration(filtered_gaze)
        calib_gaze   = None

        if calibrator.is_calibrated and not calibrator.is_calibrating:
            # Map smoothed iris gaze -> Screen Space [0.0, 1.0]
            calib_gaze = calibrator.map_to_screen(filtered_gaze)

        # ── 5. Render visualizations ──────────────────────────────────────────
        # Draw face mesh & iris dots (subtle)
        tracker.draw_landmarks(frame)
        tracker.draw_iris(frame, left_iris_px, right_iris_px)

        # If calibrating: render active calibration target
        if calib_status.get("is_calibrating"):
            ui.draw_calibration_target(frame, calib_status)
        elif calibrator.is_calibrated:
            # If calibrated: render calibrated gaze crosshair & trigger zones
            ui.draw_calibrated_gaze(frame, calib_gaze, zone_frac=ZONE_WIDTH_FRAC)

        # ── 6. FPS Calculation ────────────────────────────────────────────────
        now = time.time()
        fps = 1.0 / max(now - prev_time, 1e-9)
        prev_time = now

        # ── 7. Render Status HUD ──────────────────────────────────────────────
        ui.draw_status_hud(
            frame, fps, tracker.face_detected,
            raw_gaze, filtered_gaze, calib_gaze,
            calibrator.is_calibrated, calibrator.is_calibrating
        )

        # ── Show window ───────────────────────────────────────────────────────
        cv2.imshow(WINDOW_NAME, frame)

        # ── Key handling ──────────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break
        elif key == ord('c') or key == ord('C'):
            calibrator.start_calibration()
        elif key == ord('r') or key == ord('R'):
            calibrator.is_calibrated = False
            calibrator.is_calibrating = False
            print("[FocusLock] Calibration reset.")

    # ── Cleanup ───────────────────────────────────────────────────────────────
    cap.release()
    tracker.close()
    cv2.destroyAllWindows()
    print("[FocusLock] Stopped.")


if __name__ == "__main__":
    main()
