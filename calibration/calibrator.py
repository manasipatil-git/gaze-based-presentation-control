# calibration/calibrator.py
# ─────────────────────────────────────────────────────────────────────────────
# 5-Point Calibrator & Linear Coordinate Mapper
#
# WHY CALIBRATION IS REQUIRED (College explanation):
#   Across a computer screen, human irises physically traverse only a narrow
#   subset of the eye socket (typically between 0.35 and 0.65). Without calibration,
#   the user could never reach the screen boundaries.
#   Calibration calculates user-specific Gain (slope m) and Offset (intercept c).
#
# FORMULA:
#   X_screen = mx * Gaze_x + cx
#   Y_screen = my * Gaze_y + cy
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
        self.calibration_data = []

        # Default responsive linear mapping:
        # Centered at ~0.50 with an amplification gain of 3.5x
        self.mx = 3.5
        self.cx = -1.25  # (0.50 * 3.5 - 1.25 = 0.50)
        self.my = 4.0
        self.cy = -1.30  # (0.45 * 4.0 - 1.30 = 0.50)
        self.is_calibrated = False

        # Attempt to load previously saved calibration on startup
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

        # Collect sample for the current point
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
        Fits 1D linear equations (slope & intercept) using numpy.polyfit with safety clamping.
        """
        gaze_xs = [d["gaze"][0] for d in self.calibration_data]
        gaze_ys = [d["gaze"][1] for d in self.calibration_data]
        target_xs = [d["target"][0] for d in self.calibration_data]
        target_ys = [d["target"][1] for d in self.calibration_data]

        # Fit X axis
        if np.std(gaze_xs) > 0.005:
            fitted_mx, fitted_cx = np.polyfit(gaze_xs, target_xs, 1)
            # Safeguard: Clamp slope between 1.5 and 8.0 to prevent hypersensitivity
            if fitted_mx > 0:
                self.mx = float(np.clip(fitted_mx, 1.5, 8.0))
            else:
                self.mx = float(np.clip(fitted_mx, -8.0, -1.5))
            self.cx = float(np.mean(target_xs) - self.mx * np.mean(gaze_xs))
        else:
            # Fallback if eye movement was very narrow
            mean_gx = np.mean(gaze_xs) if len(gaze_xs) > 0 else 0.50
            self.mx = 3.5
            self.cx = float(0.50 - self.mx * mean_gx)

        # Fit Y axis
        if np.std(gaze_ys) > 0.005:
            fitted_my, fitted_cy = np.polyfit(gaze_ys, target_ys, 1)
            if fitted_my > 0:
                self.my = float(np.clip(fitted_my, 1.5, 8.0))
            else:
                self.my = float(np.clip(fitted_my, -8.0, -1.5))
            self.cy = float(np.mean(target_ys) - self.my * np.mean(gaze_ys))
        else:
            mean_gy = np.mean(gaze_ys) if len(gaze_ys) > 0 else 0.45
            self.my = 4.0
            self.cy = float(0.50 - self.my * mean_gy)

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
        """Load calibration coefficients from local JSON file if exists and valid."""
        if not os.path.exists(self.filepath):
            return False

        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)

            if data.get("is_calibrated"):
                m = data["mapping"]
                mx = m.get("mx", 1.0)
                # Ignore corrupted calibration where mx was exactly 1.0 and cx was 0.0
                if abs(mx - 1.0) < 1e-4 and abs(m.get("cx", 0.0)) < 1e-4:
                    print("[FocusLock] Detected corrupted calibration.json — resetting to dynamic default.")
                    return False

                self.mx = m["mx"]
                self.cx = m["cx"]
                self.my = m["my"]
                self.cy = m["cy"]
                self.is_calibrated = True
                print(f"[FocusLock] Loaded calibration from {self.filepath} (X gain={self.mx:.2f}, Y gain={self.my:.2f})")
                return True
        except Exception as e:
            print(f"[FocusLock] Could not load calibration: {e}")

        return False

    def map_to_screen(self, gaze_point):
        """
        Converts normalized gaze coordinates to calibrated screen coordinates [0.0, 1.0].
        Provides responsive default mapping even before custom 5-point calibration.
        """
        if gaze_point is None:
            return None

        gx, gy = gaze_point
        calib_x = self.mx * gx + self.cx
        calib_y = self.my * gy + self.cy

        # Clamp output to valid screen bounds [0.0, 1.0]
        calib_x = float(np.clip(calib_x, 0.0, 1.0))
        calib_y = float(np.clip(calib_y, 0.0, 1.0))

        return (calib_x, calib_y)
