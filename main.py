# main.py  — STAGE 6: FocusLock Complete MVP Pipeline & Data Logging
# ─────────────────────────────────────────────────────────────────────────────
# FocusLock Complete Architecture:
#   1. Sensing:       Webcam + MediaPipe Tasks FaceLandmarker (Iris landmarks)
#   2. Normalization: Relative eye-socket boundary ratio [0.0, 1.0]
#   3. Filtering:     Sliding-window moving-average filter (N=7 jitter reduction)
#   4. Calibration:   5-Point linear least-squares regression (numpy.polyfit)
#   5. Intent:        Dwell-time thresholding (1.8s) with single-shot lock
#   6. Actuation:     PyAutoGUI presentation keypress (Left/Right) with DEMO_MODE
#   7. Telemetry:     Real-time CSV data logging for scientific benchmarking
#
# Controls:
#   'd' - Toggle DEMO_MODE (Simulation vs Live Keyboard dispatch)
#   'l' - Toggle Telemetry Data Logging (Record / Pause)
#   'c' - Start / Re-run 5-point calibration
#   'r' - Reset calibration & dwell state
#   'q' / ESC - Quit & Save Telemetry
# ─────────────────────────────────────────────────────────────────────────────

import cv2
import time

from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    SMOOTHING_WINDOW,
    ZONE_WIDTH_FRAC,
    DWELL_TIME,
    DEMO_MODE,
    WINDOW_NAME,
)
from tracking.iris_tracker          import IrisTracker
from tracking.gaze_estimator        import GazeEstimator
from filtering.moving_average        import MovingAverageFilter
from calibration.calibrator         import Calibrator
from intent.dwell_detector          import DwellDetector
from control.presentation_controller import PresentationController
from data.logger                    import DataLogger
from ui.overlay                     import UIOverlay


def main():
    # ── Open webcam ───────────────────────────────────────────────────────────
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera {CAMERA_INDEX}.")
        return

    print("=" * 72)
    print("  FocusLock — Working MVP (Gaze-Controlled Presentation System)")
    print("=" * 72)
    print(f"  Dwell threshold: {DWELL_TIME}s")
    print(f"  Initial Control Mode: {'DEMO MODE (Simulation)' if DEMO_MODE else 'LIVE MODE (Keypresses Active)'}")
    print("  Controls:")
    print("    'd' - Toggle DEMO / LIVE presentation mode")
    print("    'l' - Toggle Telemetry Logging to CSV")
    print("    'c' - Run 5-point calibration")
    print("    'r' - Reset calibration")
    print("    'q' - Quit application and save logs")
    print("=" * 72)

    # ── Initialize modules ────────────────────────────────────────────────────
    tracker        = IrisTracker()
    estimator      = GazeEstimator()
    filter_        = MovingAverageFilter(window_size=SMOOTHING_WINDOW)
    calibrator     = Calibrator()
    dwell_detector = DwellDetector(dwell_time=DWELL_TIME, zone_width_frac=ZONE_WIDTH_FRAC)
    controller     = PresentationController(demo_mode=DEMO_MODE)
    logger         = DataLogger(auto_start=True)
    ui             = UIOverlay()

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
        intent_info  = None
        action       = None
        zone         = None

        if calibrator.is_calibrated and not calibrator.is_calibrating:
            # Map smoothed iris gaze -> Screen Space [0.0, 1.0]
            calib_gaze = calibrator.map_to_screen(filtered_gaze)

            # ── 5. Dwell-Based Intent Detection ───────────────────────────────
            intent_info = dwell_detector.update(calib_gaze)
            zone = intent_info.get("zone")

            # ── 6. Presentation Control Actuation (PyAutoGUI) ─────────────────
            action = intent_info.get("action_triggered")
            if action:
                controller.trigger_action(action)
        else:
            dwell_detector.reset()

        # ── 7. Telemetry Data Logging (CSV) ───────────────────────────────────
        logger.log_frame(
            raw_gaze=raw_gaze,
            filtered_gaze=filtered_gaze,
            calib_gaze=calib_gaze,
            zone=zone,
            action=action
        )

        # ── 8. Render Visualizations ──────────────────────────────────────────
        # Subtle face mesh & iris dots
        tracker.draw_landmarks(frame)
        tracker.draw_iris(frame, left_iris_px, right_iris_px)

        if calib_status.get("is_calibrating"):
            ui.draw_calibration_target(frame, calib_status)
        elif calibrator.is_calibrated:
            # Render calibrated gaze pointer, trigger zones, dwell feedback & banner
            ui.draw_calibrated_gaze(
                frame, calib_gaze,
                zone_frac=ZONE_WIDTH_FRAC,
                intent_info=intent_info,
                demo_mode=controller.demo_mode
            )

        # ── 9. FPS Calculation ────────────────────────────────────────────────
        now = time.time()
        fps = 1.0 / max(now - prev_time, 1e-9)
        prev_time = now

        # ── 10. Render Status HUD ─────────────────────────────────────────────
        ui.draw_status_hud(
            frame, fps, tracker.face_detected,
            raw_gaze, filtered_gaze, calib_gaze,
            calibrator.is_calibrated, calibrator.is_calibrating,
            intent_info=intent_info,
            demo_mode=controller.demo_mode,
            is_logging=logger.is_logging,
            log_count=logger.frame_count
        )

        # ── Show window ───────────────────────────────────────────────────────
        cv2.imshow(WINDOW_NAME, frame)

        # ── Key handling ──────────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break
        elif key == ord('d') or key == ord('D'):
            # Toggle between DEMO (safe simulation) and LIVE (real keypresses)
            controller.toggle_demo_mode()
        elif key == ord('l') or key == ord('L'):
            # Toggle Telemetry Logging
            logger.toggle_logging()
        elif key == ord('c') or key == ord('C'):
            calibrator.start_calibration()
            dwell_detector.reset()
        elif key == ord('r') or key == ord('R'):
            calibrator.is_calibrated = False
            calibrator.is_calibrating = False
            dwell_detector.reset()
            print("[FocusLock] Calibration & dwell state reset.")

    # ── Cleanup ───────────────────────────────────────────────────────────────
    logger.close()
    cap.release()
    tracker.close()
    cv2.destroyAllWindows()
    print("[FocusLock] Application stopped successfully.")


if __name__ == "__main__":
    main()
