# ui/overlay.py
# ─────────────────────────────────────────────────────────────────────────────
# HUD, Calibration Visualizer, and Calibrated Gaze Overlay using OpenCV.
#
# Features:
#   1. Status HUD with Calibration state
#   2. 5-Point Calibration Target Display (Pulsing Bullseye + Progress fill)
#   3. Fullscreen Calibrated Gaze Crosshair with subtle trigger zones
# ─────────────────────────────────────────────────────────────────────────────

import cv2
import numpy as np


class UIOverlay:
    """
    Renders status HUD, calibration targets, and calibrated gaze crosshairs.
    """

    def __init__(self):
        pass

    def draw_status_hud(self, frame, fps, face_detected, raw_gaze, filtered_gaze, calib_gaze, is_calibrated, is_calibrating):
        """
        Draws the main status information panel on the top-left corner.
        """
        h, w = frame.shape[:2]

        # Draw semi-transparent background card
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (340, 265), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.70, frame, 0.30, 0, frame)
        cv2.rectangle(frame, (10, 10), (340, 265), (80, 80, 80), 1)

        # Header
        cv2.putText(frame, "FocusLock - Stage 3", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(frame, f"FPS: {fps:.1f}", (245, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)

        # Status indicators
        face_status = "DETECTED" if face_detected else "SEARCHING..."
        face_color  = (0, 255, 0) if face_detected else (0, 0, 255)
        cv2.putText(frame, f"Face:        {face_status}", (20, 62),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, face_color, 1, cv2.LINE_AA)

        iris_status = "ACTIVE" if face_detected else "OFFLINE"
        iris_color  = (0, 255, 0) if face_detected else (100, 100, 100)
        cv2.putText(frame, f"Iris Track:  {iris_status}", (20, 82),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, iris_color, 1, cv2.LINE_AA)

        # Calibration state
        if is_calibrating:
            c_text, c_color = "IN PROGRESS...", (0, 255, 255)
        elif is_calibrated:
            c_text, c_color = "COMPLETE", (0, 255, 0)
        else:
            c_text, c_color = "PRESS 'C' TO START", (0, 165, 255)

        cv2.putText(frame, f"Calibration: {c_text}", (20, 102),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, c_color, 1, cv2.LINE_AA)

        # Divider
        cv2.line(frame, (20, 115), (330, 115), (60, 60, 60), 1)

        # Gaze coordinates
        if filtered_gaze and filtered_gaze[0] is not None:
            fx, fy = filtered_gaze
            cv2.putText(frame, f"Raw/Filter:  X:{fx:.3f}  Y:{fy:.3f}", (20, 138),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 0), 1, cv2.LINE_AA)
        else:
            cv2.putText(frame, "Raw/Filter:  --", (20, 138),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (120, 120, 120), 1, cv2.LINE_AA)

        if calib_gaze and calib_gaze[0] is not None:
            cx, cy = calib_gaze
            cv2.putText(frame, f"CALIBRATED:  X:{cx:.3f}  Y:{cy:.3f}", (20, 162),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 255), 1, cv2.LINE_AA)
        else:
            cv2.putText(frame, "CALIBRATED:  (Not calibrated)", (20, 162),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (120, 120, 120), 1, cv2.LINE_AA)

        # Instructions
        cv2.line(frame, (20, 178), (330, 178), (60, 60, 60), 1)
        cv2.putText(frame, "Press 'c' : Start Calibration", (20, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (220, 220, 220), 1, cv2.LINE_AA)
        cv2.putText(frame, "Press 'r' : Reset Calibration", (20, 222),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (180, 180, 180), 1, cv2.LINE_AA)
        cv2.putText(frame, "Press 'q' : Quit", (20, 244),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (150, 150, 150), 1, cv2.LINE_AA)

    def draw_calibration_target(self, frame, point_info):
        """
        Draws the active calibration target on screen with progress feedback.
        """
        h, w = frame.shape[:2]
        tx, ty = point_info["target_pos"]
        px = int(tx * w)
        py = int(ty * h)
        progress = point_info.get("progress", 0.0)
        point_name = point_info.get("point_name", "")
        idx = point_info.get("point_idx", 0)

        # Dim background slightly to focus attention on the target
        darkener = np.zeros_like(frame)
        cv2.addWeighted(frame, 0.65, darkener, 0.35, 0, frame)

        # Outer target ring
        cv2.circle(frame, (px, py), 28, (0, 255, 255), 2, cv2.LINE_AA)

        # Animated / Progress filling circle
        radius = int(6 + progress * 20)
        cv2.circle(frame, (px, py), radius, (0, 255, 0), -1, cv2.LINE_AA)
        cv2.circle(frame, (px, py), 3, (0, 0, 0), -1, cv2.LINE_AA)

        # Crosshair on target
        cv2.line(frame, (px - 35, py), (px + 35, py), (0, 255, 255), 1, cv2.LINE_AA)
        cv2.line(frame, (px, py - 35), (px, py + 35), (0, 255, 255), 1, cv2.LINE_AA)

        # Text prompt near target
        prompt_text = f"LOOK HERE ({idx + 1}/5: {point_name}) - {int(progress * 100)}%"
        cv2.putText(frame, prompt_text, (px - 110, py + 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

    def draw_calibrated_gaze(self, frame, calib_gaze, zone_frac=0.15):
        """
        Draws subtle trigger zones on left/right and the calibrated gaze crosshair.
        """
        h, w = frame.shape[:2]

        # 1. Draw subtle Left & Right Trigger Zones
        zone_w = int(w * zone_frac)

        # Left Zone
        left_overlay = frame.copy()
        cv2.rectangle(left_overlay, (0, 0), (zone_w, h), (255, 100, 0), -1)
        cv2.addWeighted(left_overlay, 0.12, frame, 0.88, 0, frame)
        cv2.rectangle(frame, (0, 0), (zone_w, h), (255, 120, 0), 1)
        cv2.putText(frame, "PREV SLIDE", (10, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 160, 0), 1, cv2.LINE_AA)

        # Right Zone
        right_overlay = frame.copy()
        cv2.rectangle(right_overlay, (w - zone_w, 0), (w, h), (0, 180, 255), -1)
        cv2.addWeighted(right_overlay, 0.12, frame, 0.88, 0, frame)
        cv2.rectangle(frame, (w - zone_w, 0), (w, h), (0, 200, 255), 1)
        cv2.putText(frame, "NEXT SLIDE", (w - zone_w + 10, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 1, cv2.LINE_AA)

        # 2. Draw Calibrated Gaze Pointer
        if calib_gaze and calib_gaze[0] is not None:
            cx = int(calib_gaze[0] * w)
            cy = int(calib_gaze[1] * h)

            # Highlight if inside left or right trigger zone
            in_left_zone  = (cx < zone_w)
            in_right_zone = (cx > w - zone_w)
            cursor_color  = (0, 255, 255) if (in_left_zone or in_right_zone) else (0, 255, 0)

            # Gaze crosshair + glowing circle
            cv2.circle(frame, (cx, cy), 12, cursor_color, 2, cv2.LINE_AA)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.line(frame, (cx - 20, cy), (cx + 20, cy), cursor_color, 1, cv2.LINE_AA)
            cv2.line(frame, (cx, cy - 20), (cx, cy + 20), cursor_color, 1, cv2.LINE_AA)

            # Coordinate tag
            cv2.putText(frame, f"Gaze ({calib_gaze[0]:.2f}, {calib_gaze[1]:.2f})", (cx + 15, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
