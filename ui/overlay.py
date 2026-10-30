# ui/overlay.py
# ─────────────────────────────────────────────────────────────────────────────
# HUD, Calibration Visualizer, Calibrated Gaze, Dwell & Telemetry Overlay.
#
# Features:
#   1. Status HUD with Calibration, Gaze, Intent, Dwell, Control, and Logger
#   2. 5-Point Calibration Target Display (Pulsing Bullseye + Progress fill)
#   3. Trigger Zones with live visual dwell-progress bars
#   4. Action trigger notification banner (e.g. "NEXT SLIDE [LIVE]")
# ─────────────────────────────────────────────────────────────────────────────

import cv2
import numpy as np


class UIOverlay:
    """
    Renders status HUD, calibration targets, trigger zones, dwell, and control feedback.
    """

    def __init__(self):
        pass

    def draw_status_hud(self, frame, fps, face_detected, raw_gaze, filtered_gaze, calib_gaze,
                        is_calibrated, is_calibrating, intent_info=None, demo_mode=True,
                        is_logging=True, log_count=0):
        """
        Draws the main status information panel on the top-left corner.
        """
        h, w = frame.shape[:2]

        # Draw semi-transparent background card
        panel_h = 390 if intent_info else 300
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (360, panel_h), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        cv2.rectangle(frame, (10, 10), (360, panel_h), (80, 80, 80), 1)

        # Header
        cv2.putText(frame, "FocusLock - Stage 6 (MVP)", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(frame, f"FPS: {fps:.1f}", (265, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (180, 180, 180), 1, cv2.LINE_AA)

        # Status indicators
        face_status = "DETECTED" if face_detected else "SEARCHING..."
        face_color  = (0, 255, 0) if face_detected else (0, 0, 255)
        cv2.putText(frame, f"Face:        {face_status}", (20, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, face_color, 1, cv2.LINE_AA)

        iris_status = "ACTIVE" if face_detected else "OFFLINE"
        iris_color  = (0, 255, 0) if face_detected else (100, 100, 100)
        cv2.putText(frame, f"Iris Track:  {iris_status}", (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, iris_color, 1, cv2.LINE_AA)

        # Calibration state
        if is_calibrating:
            c_text, c_color = "IN PROGRESS...", (0, 255, 255)
        elif is_calibrated:
            c_text, c_color = "COMPLETE", (0, 255, 0)
        else:
            c_text, c_color = "PRESS 'C' TO START", (0, 165, 255)

        cv2.putText(frame, f"Calibration: {c_text}", (20, 92),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, c_color, 1, cv2.LINE_AA)

        # Control Mode (DEMO vs LIVE)
        mode_text  = "DEMO (Simulation)" if demo_mode else "LIVE (Keypress Active)"
        mode_color = (0, 200, 255) if demo_mode else (0, 80, 255)
        cv2.putText(frame, f"Control:     {mode_text}", (20, 109),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, mode_color, 1, cv2.LINE_AA)

        # Data Logging state
        log_text = f"REC ({log_count} frames)" if is_logging else "PAUSED"
        log_color = (0, 255, 0) if is_logging else (140, 140, 140)
        cv2.putText(frame, f"Telemetry:   {log_text}", (20, 126),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, log_color, 1, cv2.LINE_AA)

        # Gaze coordinates
        if calib_gaze and calib_gaze[0] is not None:
            cx, cy = calib_gaze
            cv2.putText(frame, f"CALIBRATED:  X:{cx:.3f}  Y:{cy:.3f}", (20, 146),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.46, (0, 255, 255), 1, cv2.LINE_AA)
        else:
            cv2.putText(frame, "CALIBRATED:  (Not calibrated)", (20, 146),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (120, 120, 120), 1, cv2.LINE_AA)

        # Divider line
        cv2.line(frame, (20, 156), (350, 156), (60, 60, 60), 1)

        # Intent & Dwell Section
        if intent_info:
            intent_label = intent_info.get("intent_label", "NONE")
            dwell_dur = intent_info.get("dwell_duration", 0.0)
            dwell_thresh = intent_info.get("dwell_threshold", 1.8)
            progress = intent_info.get("progress", 0.0)
            banner = intent_info.get("active_action_banner")

            intent_color = (0, 255, 255) if intent_label != "NONE" else (180, 180, 180)
            cv2.putText(frame, f"Intent:      {intent_label}", (20, 178),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, intent_color, 1, cv2.LINE_AA)

            dwell_str = f"Dwell:       {dwell_dur:.1f} / {dwell_thresh:.1f} sec"
            cv2.putText(frame, dwell_str, (20, 197),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (220, 220, 220), 1, cv2.LINE_AA)

            # Mini horizontal progress bar for dwell
            bar_x, bar_y, bar_w, bar_h = 20, 206, 320, 9
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
            fill_w = int(bar_w * progress)
            fill_color = (0, 255, 0) if progress < 1.0 else (0, 255, 255)
            if fill_w > 0:
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), fill_color, -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (120, 120, 120), 1)

            # Action confirmation banner in HUD
            if banner:
                badge_text = f"ACTION: {banner} ({'DEMO' if demo_mode else 'KEYPRESS'})"
                cv2.rectangle(frame, (18, 222), (352, 248), (0, 140, 0) if demo_mode else (0, 100, 200), -1)
                cv2.rectangle(frame, (18, 222), (352, 248), (0, 255, 0), 1)
                cv2.putText(frame, badge_text, (24, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.46, (255, 255, 255), 1, cv2.LINE_AA)
                y_offset = 272
            else:
                y_offset = 234
        else:
            y_offset = 175

        # Instructions
        cv2.line(frame, (20, y_offset - 6), (350, y_offset - 6), (60, 60, 60), 1)
        cv2.putText(frame, "Press 'd' : Toggle Demo / Live Mode", (20, y_offset + 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 200, 100), 1, cv2.LINE_AA)
        cv2.putText(frame, "Press 'l' : Toggle Telemetry Logging", (20, y_offset + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (100, 255, 150), 1, cv2.LINE_AA)
        cv2.putText(frame, "Press 'c' : Calibrate", (20, y_offset + 44),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(frame, "Press 'r' : Reset Calib", (20, y_offset + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 180, 180), 1, cv2.LINE_AA)
        cv2.putText(frame, "Press 'q' : Quit", (20, y_offset + 76),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (150, 150, 150), 1, cv2.LINE_AA)

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

        # Dim background slightly to focus attention on target
        darkener = np.zeros_like(frame)
        cv2.addWeighted(frame, 0.65, darkener, 0.35, 0, frame)

        # Outer target ring
        cv2.circle(frame, (px, py), 28, (0, 255, 255), 2, cv2.LINE_AA)

        # Animated progress filling circle
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

    def draw_calibrated_gaze(self, frame, calib_gaze, zone_frac=0.15, intent_info=None, demo_mode=True):
        """
        Draws trigger zones on left/right edges with dwell progress and calibrated gaze pointer.
        """
        h, w = frame.shape[:2]
        zone_w = int(w * zone_frac)

        current_zone = intent_info.get("zone") if intent_info else None
        dwell_progress = intent_info.get("progress", 0.0) if intent_info else 0.0
        active_action = intent_info.get("active_action_banner") if intent_info else None

        # ── 1. Left Trigger Zone ──────────────────────────────────────────────
        is_left_active = (current_zone == "LEFT")
        left_overlay = frame.copy()
        left_color = (0, 200, 255) if is_left_active else (255, 100, 0)
        left_alpha = 0.25 if is_left_active else 0.10

        cv2.rectangle(left_overlay, (0, 0), (zone_w, h), left_color, -1)
        cv2.addWeighted(left_overlay, left_alpha, frame, 1.0 - left_alpha, 0, frame)
        cv2.rectangle(frame, (0, 0), (zone_w, h), left_color, 2 if is_left_active else 1)
        cv2.putText(frame, "PREV SLIDE", (10, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, left_color, 2 if is_left_active else 1, cv2.LINE_AA)

        # Left zone vertical dwell progress bar
        if is_left_active and dwell_progress > 0.0:
            prog_h = int(h * dwell_progress)
            cv2.rectangle(frame, (zone_w - 8, h - prog_h), (zone_w, h), (0, 255, 0), -1)

        # ── 2. Right Trigger Zone ─────────────────────────────────────────────
        is_right_active = (current_zone == "RIGHT")
        right_overlay = frame.copy()
        right_color = (0, 200, 255) if is_right_active else (0, 180, 255)
        right_alpha = 0.25 if is_right_active else 0.10

        cv2.rectangle(right_overlay, (w - zone_w, 0), (w, h), right_color, -1)
        cv2.addWeighted(right_overlay, right_alpha, frame, 1.0 - right_alpha, 0, frame)
        cv2.rectangle(frame, (w - zone_w, 0), (w, h), right_color, 2 if is_right_active else 1)
        cv2.putText(frame, "NEXT SLIDE", (w - zone_w + 10, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, right_color, 2 if is_right_active else 1, cv2.LINE_AA)

        # Right zone vertical dwell progress bar
        if is_right_active and dwell_progress > 0.0:
            prog_h = int(h * dwell_progress)
            cv2.rectangle(frame, (w - zone_w, h - prog_h), (w - zone_w + 8, h), (0, 255, 0), -1)

        # ── 3. Calibrated Gaze Cursor ─────────────────────────────────────────
        if calib_gaze and calib_gaze[0] is not None:
            cx = int(calib_gaze[0] * w)
            cy = int(calib_gaze[1] * h)

            in_zone = (current_zone is not None)
            cursor_color = (0, 255, 255) if in_zone else (0, 255, 0)

            # Cursor crosshair + glowing ring
            cv2.circle(frame, (cx, cy), 12, cursor_color, 2, cv2.LINE_AA)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.line(frame, (cx - 20, cy), (cx + 20, cy), cursor_color, 1, cv2.LINE_AA)
            cv2.line(frame, (cx, cy - 20), (cx, cy + 20), cursor_color, 1, cv2.LINE_AA)

            # Dwell progress arc orbiting cursor
            if in_zone and dwell_progress > 0.0:
                axes = (22, 22)
                angle = 0
                start_angle = 0
                end_angle = int(360 * dwell_progress)
                cv2.ellipse(frame, (cx, cy), axes, angle, start_angle, end_angle, (0, 255, 0), 3, cv2.LINE_AA)

            # Coordinate tag
            cv2.putText(frame, f"({calib_gaze[0]:.2f}, {calib_gaze[1]:.2f})", (cx + 15, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # ── 4. Large Action Trigger Notification Banner ───────────────────────
        if active_action:
            mode_tag = "[DEMO]" if demo_mode else "[LIVE KEYPRESS]"
            banner_text = f"{active_action} {mode_tag}"
            text_size, _ = cv2.getTextSize(banner_text, cv2.FONT_HERSHEY_SIMPLEX, 0.85, 2)
            bx = (w - text_size[0]) // 2
            by = 60

            banner_bg = (0, 140, 0) if demo_mode else (0, 80, 200)
            cv2.rectangle(frame, (bx - 20, by - 35), (bx + text_size[0] + 20, by + 15), banner_bg, -1)
            cv2.rectangle(frame, (bx - 20, by - 35), (bx + text_size[0] + 20, by + 15), (0, 255, 0), 2)
            cv2.putText(frame, banner_text, (bx, by),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)
