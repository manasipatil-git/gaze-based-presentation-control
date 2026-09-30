# calibration/calibrator.py
# ─────────────────────────────────────────────────────────────────────────────
# 5-Point Calibrator & Linear Coordinate Mapper
#
# WHY CALIBRATION IS REQUIRED (College explanation):
#   Every human's eyes and webcams are positioned differently.
#   A user looking at the top-left of their monitor might produce a raw normalized
#   gaze of (0.42, 0.45) rather than (0.0, 0.0).
#
#   Calibration records the raw iris values at 5 known target locations:
#     1. Top-Left     (0.1, 0.1)
#     2. Top-Right    (0.9, 0.1)
#     3. Center       (0.5, 0.5)
#     4. Bottom-Left  (0.1, 0.9)
#     5. Bottom-Right (0.9, 0.9)
#
# MAPPING FORMULA (Linear 1D per axis using NumPy polyfit):
#   X_screen = m_x * Gaze_x + c_x
#   Y_screen = m_y * Gaze_y + c_y
#
#   Where (m_x, c_x) and (m_y, c_y) are the slope (gain) and intercept (offset).
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
import numpy as np
from config import CALIBRATION_FILE, CALIBRATION_SAMPLES


class Calibrator:
    """
    Manages 5-point calibration workflow and applies linear coordinate mapping.
    """

    # 5 standard calibration screen positions (normalized in [0.0, 1.0])
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

        # Stored calibration data pairs: list of {"target": (tx, ty), "gaze": (gx, gy)}
        self.calibration_data = []

        # Linear mapping parameters: X_screen = mx * gx + cx
        self.mx = 1.0
        self.cx = 0.0
        self.my = 1.0
        self.cy = 0.0
        self.is_calibrated = False

        # Attempt to load previously saved calibration on startup
        self.load_calibration()

    def start_calibration(self):
        """Begin the 5-point calibration procedure."""
        self.is_calibrating = True
        self.current_point_idx = 0
        self._current_samples = []
        self.calibration_data = []
        print("[FocusLock] Calibration started. Look at each target on screen.")

    def update_calibration(self, gaze_point):
        """
        Feed the current smoothed gaze point into the calibrator.

        Returns
        -------
        dict with status:
          {
             "is_calibrating": bool,
             "point_idx": int,
             "point_name": str,
             "target_pos": (tx, ty),
             "progress": float (0.0 to 1.0),
             "completed_just_now": bool
          }
        """
        if not self.is_calibrating:
            return {"is_calibrating": False}

        if gaze_point is None:
            # Cannot sample if eyes are not tracked
            return {
                "is_calibrating": True,
                "point_idx": self.current_point_idx,
                "point_name": self.POINTS[self.current_point_idx]["name"],
                "target_pos": self.POINTS[self.current_point_idx]["pos"],
                "progress": len(self._current_samples) / float(self.samples_per_point),
                "completed_just_now": False
            }

        # Collect sample for the current point
        self._current_samples.append(gaze_point)
        progress = len(self._current_samples) / float(self.samples_per_point)

        # Once we have enough samples for this point
        if len(self._current_samples) >= self.samples_per_point:
            # Compute average gaze for this target point
            xs = [p[0] for p in self._current_samples]
            ys = [p[1] for p in self._current_samples]
            avg_gaze = (float(np.mean(xs)), float(np.mean(ys)))

            target_pos = self.POINTS[self.current_point_idx]["pos"]
            self.calibration_data.append({
                "point_name": self.POINTS[self.current_point_idx]["name"],
                "target": target_pos,
                "gaze": avg_gaze
            })

            print(f"[FocusLock] Point {self.current_point_idx + 1}/5 ({self.POINTS[self.current_point_idx]['name']}) recorded.")

            # Move to next target point
            self.current_point_idx += 1
            self._current_samples = []

            # If all 5 points are done
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
        Fits 1D linear equations (slope & intercept) using numpy.polyfit.
        Target_X = mx * Gaze_X + cx
        Target_Y = my * Gaze_Y + cy
        """
        gaze_xs = [d["gaze"][0] for d in self.calibration_data]
        gaze_ys = [d["gaze"][1] for d in self.calibration_data]
        target_xs = [d["target"][0] for d in self.calibration_data]
        target_ys = [d["target"][1] for d in self.calibration_data]

        # 1st-degree polynomial fit (Linear line fit)
        # Avoid division by zero if iris movement was very small
        if np.std(gaze_xs) > 1e-4:
            self.mx, self.cx = np.polyfit(gaze_xs, target_xs, 1)
        else:
            self.mx, self.cx = 1.0, 0.0

        if np.std(gaze_ys) > 1e-4:
            self.my, self.cy = np.polyfit(gaze_ys, target_ys, 1)
        else:
            self.my, self.cy = 1.0, 0.0

        self.is_calibrated = True

        # Save to JSON file
        payload = {
            "is_calibrated": True,
            "mapping": {
                "mx": float(self.mx),
                "cx": float(self.cx),
                "my": float(self.my),
                "cy": float(self.cy)
            },
            "points": self.calibration_data
        }

        with open(self.filepath, "w") as f:
            json.dump(payload, f, indent=2)

        print(f"[FocusLock] Calibration saved to {self.filepath}")
        print(f"  X-mapping: Target_X = {self.mx:.3f} * Gaze_X + ({self.cx:.3f})")
        print(f"  Y-mapping: Target_Y = {self.my:.3f} * Gaze_Y + ({self.cy:.3f})")

    def load_calibration(self):
        """Load calibration coefficients from local JSON file if exists."""
        if not os.path.exists(self.filepath):
            return False

        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)

            if data.get("is_calibrated"):
                m = data["mapping"]
                self.mx = m["mx"]
                self.cx = m["cx"]
                self.my = m["my"]
                self.cy = m["cy"]
                self.is_calibrated = True
                print(f"[FocusLock] Loaded existing calibration from {self.filepath}")
                return True
        except Exception as e:
            print(f"[FocusLock] Could not load calibration: {e}")

        return False

    def map_to_screen(self, gaze_point):
        """
        Converts normalized gaze coordinates to calibrated screen coordinates [0.0, 1.0].

        Parameters
        ----------
        gaze_point : tuple (gx, gy)

        Returns
        -------
        tuple (calib_x, calib_y) in [0.0, 1.0], or None
        """
        if gaze_point is None or not self.is_calibrated:
            return None

        gx, gy = gaze_point
        calib_x = self.mx * gx + self.cx
        calib_y = self.my * gy + self.cy

        # Clamp output to valid screen bounds [0.0, 1.0]
        calib_x = float(np.clip(calib_x, 0.0, 1.0))
        calib_y = float(np.clip(calib_y, 0.0, 1.0))

        return (calib_x, calib_y)
