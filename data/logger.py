# data/logger.py
# ─────────────────────────────────────────────────────────────────────────────
# DataLogger: Frame-by-frame telemetry recording for scientific benchmarking.
#
# PURPOSE (College explanation):
#   To quantitatively demonstrate to evaluators that your pipeline improves
#   signal stability and accurately detects dwell intent, real telemetry data
#   is essential.
#
# FIELDS RECORDED PER FRAME:
#   - timestamp    : Wall-clock epoch timestamp (seconds)
#   - raw_x, raw_y : Normalized gaze coordinates directly from sensor (noisy)
#   - filtered_x, filtered_y : Coordinates after moving-average filter (smoothed)
#   - calibrated_x, calibrated_y : Coordinates mapped into screen bounds [0.0, 1.0]
#   - zone         : Active interaction zone ('LEFT', 'RIGHT', or 'NONE')
#   - action       : Triggered intent command ('NEXT_SLIDE', 'PREV_SLIDE', or '')
#
# NOTE: No synthetic or fabricated data is ever recorded.
# ─────────────────────────────────────────────────────────────────────────────

import os
import csv
import time
from config import LOG_DIR, LOG_FILE


class DataLogger:
    """
    Records live eye-tracking telemetry to CSV for post-session empirical analysis.
    """

    def __init__(self, log_dir: str = LOG_DIR, log_file: str = LOG_FILE, auto_start: bool = True):
        self.log_dir = log_dir
        self.log_file = log_file
        self.filepath = os.path.join(self.log_dir, self.log_file)
        self.is_logging = auto_start
        self.frame_count = 0
        self._file = None
        self._writer = None

        self._ensure_log_directory()
        if self.is_logging:
            self._open_file()

    def _ensure_log_directory(self):
        """Creates the data/logs directory if it does not exist."""
        os.makedirs(self.log_dir, exist_ok=True)

    def _open_file(self):
        """Opens CSV file and writes header row."""
        self._ensure_log_directory()
        file_exists = os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0
        
        # Open in append mode so multiple runs can append or start fresh
        self._file = open(self.filepath, mode="w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)

        # CSV Header
        self._writer.writerow([
            "timestamp",
            "raw_x", "raw_y",
            "filtered_x", "filtered_y",
            "calibrated_x", "calibrated_y",
            "zone",
            "action"
        ])
        self._file.flush()

    def log_frame(self, raw_gaze, filtered_gaze, calib_gaze, zone=None, action=None):
        """
        Record a single frame's telemetry.

        Parameters
        ----------
        raw_gaze : tuple of (float, float) or None
        filtered_gaze : tuple of (float, float) or None
        calib_gaze : tuple of (float, float) or None
        zone : str or None ('LEFT', 'RIGHT', None)
        action : str or None ('NEXT_SLIDE', 'PREV_SLIDE', None)
        """
        if not self.is_logging or self._writer is None:
            return

        ts = f"{time.time():.4f}"

        rx = f"{raw_gaze[0]:.4f}" if raw_gaze and raw_gaze[0] is not None else ""
        ry = f"{raw_gaze[1]:.4f}" if raw_gaze and raw_gaze[1] is not None else ""

        fx = f"{filtered_gaze[0]:.4f}" if filtered_gaze and filtered_gaze[0] is not None else ""
        fy = f"{filtered_gaze[1]:.4f}" if filtered_gaze and filtered_gaze[1] is not None else ""

        cx = f"{calib_gaze[0]:.4f}" if calib_gaze and calib_gaze[0] is not None else ""
        cy = f"{calib_gaze[1]:.4f}" if calib_gaze and calib_gaze[1] is not None else ""

        z = zone if zone else "NONE"
        act = action if action else ""

        self._writer.writerow([ts, rx, ry, fx, fy, cx, cy, z, act])
        self.frame_count += 1

        # Periodically flush every 30 frames (~1 sec) to save data even if aborted
        if self.frame_count % 30 == 0:
            self._file.flush()

    def toggle_logging(self):
        """Toggle recording state on/off."""
        self.is_logging = not self.is_logging
        if self.is_logging and self._file is None:
            self._open_file()
        status = "RECORDING" if self.is_logging else "PAUSED"
        print(f"[FocusLock Logger] Data logging: {status} ({self.frame_count} frames logged)")
        return self.is_logging

    def close(self):
        """Flush and safely close the CSV file."""
        if self._file:
            self._file.flush()
            self._file.close()
            self._file = None
            self._writer = None
            print(f"[FocusLock Logger] Saved {self.frame_count} frames to {self.filepath}")
