# tracking/gaze_estimator.py
# ─────────────────────────────────────────────────────────────────────────────
# GazeEstimator converts raw iris pixel positions into a normalised gaze vector.
#
# WHAT "NORMALISED" MEANS HERE:
#   We calculate a scale-invariant ratio [0.0, 1.0] that represents where
#   the iris is positioned relative to the eye bounding box (the eye socket).
#
# PHYSIOLOGICAL RANGE EXPANSION (Key for accuracy):
#   Because the iris has a physical radius (~12px) and the eye socket has
#   anatomical limits, the iris center physically travels only within
#   approximately [0.28, 0.72] of the eye width.
#   If we don't expand this range, looking left/right only yields ~0.35-0.65,
#   making screen trigger zones hard to reach without excessive head movement.
#   We linearly map [0.28, 0.72] -> [0.0, 1.0] so natural glances easily reach edges!
#
# DUAL-EYE FUSION:
#   Averages normalized vectors from both eyes to eliminate unilateral landmark noise.
# ─────────────────────────────────────────────────────────────────────────────

import numpy as np


class GazeEstimator:
    """
    Converts iris pixel position -> normalised gaze (x, y) in [0.0, 1.0].
    """

    def _normalize_single_eye(self, iris_px, eye_bbox):
        """
        Calculates normalized (x, y) for a single eye with physiological range expansion.
        """
        if iris_px is None or eye_bbox is None:
            return None

        x_min, y_min, x_max, y_max = eye_bbox
        iris_x, iris_y = iris_px

        eye_w = x_max - x_min
        eye_h = y_max - y_min

        if eye_w <= 0 or eye_h <= 0:
            return None

        # 1. Normalized position relative to eyelid bounds [0.0, 1.0]
        raw_norm_x = (iris_x - x_min) / float(eye_w)
        raw_norm_y = (iris_y - y_min) / float(eye_h)

        # 2. Physiological excursion expansion:
        # Map physical iris travel span [0.28, 0.72] -> full [0.0, 1.0]
        span_min_x, span_max_x = 0.28, 0.72
        norm_x = (raw_norm_x - span_min_x) / (span_max_x - span_min_x)

        span_min_y, span_max_y = 0.28, 0.72
        norm_y = (raw_norm_y - span_min_y) / (span_max_y - span_min_y)

        # 3. Clamp output to valid bounds [0.0, 1.0]
        norm_x = float(np.clip(norm_x, 0.0, 1.0))
        norm_y = float(np.clip(norm_y, 0.0, 1.0))

        return (norm_x, norm_y)

    def estimate(self, left_iris_px, left_eye_bbox, right_iris_px=None, right_eye_bbox=None):
        """
        Estimate normalized gaze point combining both eyes.

        Parameters
        ----------
        left_iris_px : tuple (x, y)
        left_eye_bbox : tuple (x_min, y_min, x_max, y_max)
        right_iris_px : tuple (x, y), optional
        right_eye_bbox : tuple (x_min, y_min, x_max, y_max), optional

        Returns
        -------
        (gaze_x, gaze_y) as floats in [0.0, 1.0], or (None, None)
        """
        gaze_left  = self._normalize_single_eye(left_iris_px, left_eye_bbox)
        gaze_right = self._normalize_single_eye(right_iris_px, right_eye_bbox)

        if gaze_left is not None and gaze_right is not None:
            avg_x = (gaze_left[0] + gaze_right[0]) / 2.0
            avg_y = (gaze_left[1] + gaze_right[1]) / 2.0
            return avg_x, avg_y
        elif gaze_left is not None:
            return gaze_left
        elif gaze_right is not None:
            return gaze_right
        else:
            return None, None
