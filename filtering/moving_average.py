# filtering/moving_average.py
# ─────────────────────────────────────────────────────────────────────────────
# MovingAverageFilter: Smooths noisy stream of (x, y) coordinates.
#
# WHY WE NEED THIS (College explanation):
#   Webcam-based iris detection suffers from high-frequency jitter caused by:
#     1. Sensor noise & low camera resolution
#     2. Subtle involuntary eye movements (microsaccades)
#     3. MediaPipe predicting landmark positions independently per-frame
#
# HOW MOVING AVERAGE WORKS:
#   Maintains a sliding window of the last N coordinates.
#   Filtered point = sum(points in window) / N
#
# TRADE-OFF TO EXPLAIN TO PROFESSOR:
#   - Larger window (e.g. N=15) -> Smoother gaze, but introduces visual lag/latency.
#   - Smaller window (e.g. N=3) -> Fast response, but more jitter.
#   - Window of N=5 to 10 is usually the sweet spot for basic webcam interaction.
# ─────────────────────────────────────────────────────────────────────────────

from collections import deque
import numpy as np


class MovingAverageFilter:
    """
    Sliding window moving average filter for 2D coordinate streams (x, y).
    """

    def __init__(self, window_size: int = 7):
        """
        Parameters
        ----------
        window_size : int
            Number of consecutive frames to average over.
        """
        self.window_size = max(1, window_size)
        self._history = deque(maxlen=self.window_size)

    def update(self, point):
        """
        Add a new (x, y) coordinate and return the smoothed (x, y).

        Parameters
        ----------
        point : tuple of (float, float) or None

        Returns
        -------
        tuple of (float, float) or None if input is invalid.
        """
        if point is None or point[0] is None or point[1] is None:
            return None

        # Append new point to sliding window (oldest point auto-evicted by deque)
        self._history.append(point)

        # Calculate mean across the current window
        xs = [p[0] for p in self._history]
        ys = [p[1] for p in self._history]

        smoothed_x = float(np.mean(xs))
        smoothed_y = float(np.mean(ys))

        return smoothed_x, smoothed_y

    def reset(self):
        """Clear filter history (e.g. when face is lost or new interaction begins)."""
        self._history.clear()

    @property
    def current_history_size(self):
        """Returns how many frames are currently buffered in the window."""
        return len(self._history)
