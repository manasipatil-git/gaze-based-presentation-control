# tracking/gaze_estimator.py
# ─────────────────────────────────────────────────────────────────────────────
# GazeEstimator converts raw iris pixel positions into a normalised gaze vector.
#
# WHAT "NORMALISED" MEANS HERE:
#   We calculate a unitless ratio [0.0, 1.0] that represents where the iris
#   is positioned relative to the eye bounding box (the eye socket).
#
# FORMULA:
#   normalized_x = (iris_x - eye_min_x) / (eye_max_x - eye_min_x)
#   normalized_y = (iris_y - eye_min_y) / (eye_max_y - eye_min_y)
#
# DUAL-EYE FUSION:
#   When both eyes are detected, we calculate normalized gaze for each eye
#   individually and take their average:
#     gaze_x = (gaze_left_x + gaze_right_x) / 2
#     gaze_y = (gaze_left_y + gaze_right_y) / 2
#   This reduces landmark errors and increases signal reliability.
# ─────────────────────────────────────────────────────────────────────────────

import numpy as np


class GazeEstimator:
    """
    Converts iris pixel position -> normalised gaze (x, y) in [0.0, 1.0].
    """

    def _normalize_single_eye(self, iris_px, eye_bbox):
        """
        Calculates normalized (x, y) for a single eye.
        """
        if iris_px is None or eye_bbox is None:
            return None

        x_min, y_min, x_max, y_max = eye_bbox
        iris_x, iris_y = iris_px

        eye_w = x_max - x_min
        eye_h = y_max - y_min

        if eye_w <= 0 or eye_h <= 0:
            return None

        # Normalized coordinates relative to eye boundaries
        norm_x = (iris_x - x_min) / float(eye_w)
        norm_y = (iris_y - y_min) / float(eye_h)

        # Clamp to [0.0, 1.0] to prevent boundary overshoots
        norm_x = float(np.clip(norm_x, 0.0, 1.0))
        norm_y = float(np.clip(norm_y, 0.0, 1.0))

        return (norm_x, norm_y)

    def estimate(self, left_iris_px, left_eye_bbox, right_iris_px=None, right_eye_bbox=None):
        """
        Estimate normalized gaze point combining both eyes if available.

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
            # Average both eyes
            avg_x = (gaze_left[0] + gaze_right[0]) / 2.0
            avg_y = (gaze_left[1] + gaze_right[1]) / 2.0
            return avg_x, avg_y
        elif gaze_left is not None:
            return gaze_left
        elif gaze_right is not None:
            return gaze_right
        else:
            return None, None
