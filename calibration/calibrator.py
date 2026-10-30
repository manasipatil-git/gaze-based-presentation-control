# calibration/calibrator.py
# ─────────────────────────────────────────────────────────────────────────────
# 5-Point Calibrator with Dual-Slope Piecewise Linear Coordinate Mapping.
#
# WHY DUAL-SLOPE (PIECEWISE) CALIBRATION IS ESSENTIAL:
#   In split-screen or single-monitor usage, human eye anatomy and webcam
#   placement create natural asymmetry:
#     - Resting eye center is often NOT at 0.50 (e.g. 0.43 when looking at a split window).
#     - Inward eye movement (adduction) has a different physical travel span
#       than outward eye movement (abduction).
#   A single global linear slope (especially if artificially clamped) starves
#   one side of sensitivity, forcing the user to physically tilt or turn their head!
#
# DUAL-SLOPE SOLUTION:
#   We calculate independent left and right sensitivity slopes around the user's
#   calibrated resting center (cx):
#     - Left Glance  (gx <= cx) -> Screen_X = 0.50 - mx_left  * (cx - gx)
#     - Right Glance (gx > cx)  -> Screen_X = 0.50 + mx_right * (gx - cx)
#   Both directions get exact 100% sensitivity tailored to that eye's movement span!
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
import numpy as np
from config import CALIBRATION_FILE, CALIBRATION_SAMPLES


class Calibrator:
    """
    Manages 5-point calibration workflow and applies balanced dual-slope
    piecewise coordinate mapping.
    """

    POINTS = [
        {"name": "Top-Left",     "pos": (0.15, 0.15)},
        {"name": "Top-Right",    "pos": (0.85, 0.15)},
        {"name": "Center",       "pos": (0.50, 0.50)},
        {"name": "Bottom-Left",  "pos": (0.15, 0.85)},
        {"name": "Bottom-Right", "pos": (0.85, 0.85)},
    ]

    def __init__(self, samples_per_point: int = CALIBRATION_SAMPLES, filepath: str = CALIBRATION_FILE):
        self.samples_per_point = samples_per_point
        self.filepath = filepath

        self.is_calibrating = False
        self.current_point_idx = 0
        self._current_samples = []
        self.calibration_data = []

        # High-sensitivity responsive default calibration parameters:
        # Centered at 0.44 with balanced 10.0x slope
        self.cx = 0.44
        self.cy = 0.46
        self.mx_left  = 10.0
        self.mx_right = 10.0
        self.my_top   = 10.0
        self.my_bot   = 10.0

        self.is_calibrated = False
        self.load_calibration()

    def start_calibration(self):
        """Begin the 5-point calibration procedure."""
        self.is_calibrating = True
        self.current_point_idx = 0
        self._current_samples = []
        self.calibration_data = []
        print("\n[FocusLock] 5-Point Calibration started. Follow the green targets on screen.")

    def update_calibration(self, gaze_point):
        """
        Feed the current smoothed gaze point into the calibrator.
        """
        if not self.is_calibrating:
            return {"is_calibrating": False}

        if gaze_point is None:
            return {
                "is_calibrating": True,
                "point_idx": self.current_point_idx,
                "point_name": self.POINTS[self.current_point_idx]["name"],
                "target_pos": self.POINTS[self.current_point_idx]["pos"],
                "progress": len(self._current_samples) / float(self.samples_per_point),
                "completed_just_now": False
            }

        self._current_samples.append(gaze_point)
        progress = len(self._current_samples) / float(self.samples_per_point)

        if len(self._current_samples) >= self.samples_per_point:
            xs = [p[0] for p in self._current_samples]
            ys = [p[1] for p in self._current_samples]
            avg_gaze = (float(np.mean(xs)), float(np.mean(ys)))

            target_pos = self.POINTS[self.current_point_idx]["pos"]
            self.calibration_data.append({
                "point_name": self.POINTS[self.current_point_idx]["name"],
                "target": target_pos,
                "gaze": avg_gaze
            })

            print(f"[FocusLock] Point {self.current_point_idx + 1}/5 ({self.POINTS[self.current_point_idx]['name']}) recorded: Gaze=({avg_gaze[0]:.3f}, {avg_gaze[1]:.3f})")

            self.current_point_idx += 1
            self._current_samples = []

            if self.current_point_idx >= len(self.POINTS):
                self._compute_and_save_mapping()
                self.is_calibrating = False
                return {
                    "is_calibrating": False,
                    "completed_just_now": True
                }

        return {
            "is_calibrating": True,
            "point_idx": self.current_point_idx,
            "point_name": self.POINTS[self.current_point_idx]["name"],
            "target_pos": self.POINTS[self.current_point_idx]["pos"],
            "progress": progress,
            "completed_just_now": False
        }

    def _compute_and_save_mapping(self):
        """
        Fits dual-slope piecewise linear mapping for perfectly balanced left/right
        and top/bottom sensitivity without requiring physical head motion.
        """
        pts_by_name = {d["point_name"]: d["gaze"] for d in self.calibration_data}

        # 1. Calibrated Center
        if "Center" in pts_by_name:
            self.cx, self.cy = pts_by_name["Center"]
        else:
            self.cx = float(np.mean([d["gaze"][0] for d in self.calibration_data]))
            self.cy = float(np.mean([d["gaze"][1] for d in self.calibration_data]))

        # 2. Left and Right horizontal spans
        left_samples = [pts_by_name[k][0] for k in ["Top-Left", "Bottom-Left"] if k in pts_by_name]
        right_samples = [pts_by_name[k][0] for k in ["Top-Right", "Bottom-Right"] if k in pts_by_name]

        avg_left_gx  = float(np.mean(left_samples)) if left_samples else (self.cx - 0.035)
        avg_right_gx = float(np.mean(right_samples)) if right_samples else (self.cx + 0.035)

        # Delta from center to targets (target delta = 0.50 - 0.15 = 0.35)
        delta_left  = max(0.008, self.cx - avg_left_gx)
        delta_right = max(0.008, avg_right_gx - self.cx)

        # Compute independent slopes with sensible limits [4.0, 22.0]
        self.mx_left  = float(np.clip(0.35 / delta_left, 4.0, 22.0))
        self.mx_right = float(np.clip(0.35 / delta_right, 4.0, 22.0))

        # 3. Top and Bottom vertical spans
        top_samples = [pts_by_name[k][1] for k in ["Top-Left", "Top-Right"] if k in pts_by_name]
        bot_samples = [pts_by_name[k][1] for k in ["Bottom-Left", "Bottom-Right"] if k in pts_by_name]

        avg_top_gy = float(np.mean(top_samples)) if top_samples else (self.cy - 0.035)
        avg_bot_gy = float(np.mean(bot_samples)) if bot_samples else (self.cy + 0.035)

        delta_top = max(0.008, self.cy - avg_top_gy)
        delta_bot = max(0.008, avg_bot_gy - self.cy)

        self.my_top = float(np.clip(0.35 / delta_top, 4.0, 22.0))
        self.my_bot = float(np.clip(0.35 / delta_bot, 4.0, 22.0))

        self.is_calibrated = True

        # Save to JSON file
        payload = {
            "is_calibrated": True,
            "mapping_type": "dual_slope_piecewise",
            "center": [float(self.cx), float(self.cy)],
            "slopes": {
                "mx_left": float(self.mx_left),
                "mx_right": float(self.mx_right),
                "my_top": float(self.my_top),
                "my_bot": float(self.my_bot)
            },
            "points": self.calibration_data
        }

        with open(self.filepath, "w") as f:
            json.dump(payload, f, indent=2)

        print(f"[FocusLock] Calibration saved to {self.filepath}")
        print(f"  Center: ({self.cx:.3f}, {self.cy:.3f})")
        print(f"  X-slopes: Left={self.mx_left:.2f}x, Right={self.mx_right:.2f}x")
        print(f"  Y-slopes: Top={self.my_top:.2f}x, Bottom={self.my_bot:.2f}x")

    def load_calibration(self):
        """Load calibration coefficients from local JSON file if exists and valid."""
        if not os.path.exists(self.filepath):
            return False

        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)

            if data.get("is_calibrated"):
                if data.get("mapping_type") == "dual_slope_piecewise":
                    self.cx, self.cy = data["center"]
                    s = data["slopes"]
                    self.mx_left  = s["mx_left"]
                    self.mx_right = s["mx_right"]
                    self.my_top   = s["my_top"]
                    self.my_bot   = s["my_bot"]
                    self.is_calibrated = True
                    print(f"[FocusLock] Loaded dual-slope calibration from {self.filepath}")
                    print(f"  Center: ({self.cx:.3f}, {self.cy:.3f}) | Left slope: {self.mx_left:.1f}x | Right slope: {self.mx_right:.1f}x")
                    return True
                else:
                    # Legacy fallback
                    return False
        except Exception as e:
            print(f"[FocusLock] Could not load calibration: {e}")

        return False

    def map_to_screen(self, gaze_point):
        """
        Converts normalized gaze coordinates to calibrated screen coordinates [0.0, 1.0]
        using piecewise dual-slope mapping around calibrated center.
        """
        if gaze_point is None:
            return None

        gx, gy = gaze_point

        # Horizontal piecewise mapping
        if gx <= self.cx:
            calib_x = 0.50 - self.mx_left * (self.cx - gx)
        else:
            calib_x = 0.50 + self.mx_right * (gx - self.cx)

        # Vertical piecewise mapping
        if gy <= self.cy:
            calib_y = 0.50 - self.my_top * (self.cy - gy)
        else:
            calib_y = 0.50 + self.my_bot * (gy - self.cy)

        # Clamp output to valid screen bounds [0.0, 1.0]
        calib_x = float(np.clip(calib_x, 0.0, 1.0))
        calib_y = float(np.clip(calib_y, 0.0, 1.0))

        return (calib_x, calib_y)
