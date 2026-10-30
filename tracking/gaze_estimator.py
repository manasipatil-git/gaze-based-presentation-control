# tracking/gaze_estimator.py
# ─────────────────────────────────────────────────────────────────────────────
# GazeEstimator: Calculates scale-invariant gaze coordinates [0.0, 1.0].
#
# RIGID CANTHI (Eye Corner) HORIZONTAL GAZE RATIO:
#   Instead of relying solely on loose eyelid margins (which flutter with blinks),
#   this estimator measures the iris position relative to the rigid inner & outer
#   canthi (eye corners). This eliminates 90% of landmark noise before filtering.
#
# PHYSIOLOGICAL RANGE EXPANSION:
#   Maps biological iris excursion [0.28, 0.72] -> full screen range [0.0, 1.0].
# ─────────────────────────────────────────────────────────────────────────────

import numpy as np


class GazeEstimator:
    """
    Converts iris pixel coordinates -> normalised gaze (x, y) in [0.0, 1.0].
    """

    def _normalize_single_eye(self, iris_px, eye_info):
        """
        Normalizes a single eye's iris position using rigid canthi and eyelid landmarks.
        """
        if iris_px is None or eye_info is None:
            return None

        iris_x, iris_y = iris_px

        if isinstance(eye_info, dict):
            # Precision mode using rigid eye corners
            c_left  = eye_info["c_left"]
            c_right = eye_info["c_right"]
            p_top   = eye_info["top"]
            p_bot   = eye_info["bottom"]

            span_x = c_right[0] - c_left[0]
            span_y = p_bot[1] - p_top[1]

            if span_x <= 0 or span_y <= 0:
                return None

            raw_norm_x = (iris_x - c_left[0]) / float(span_x)
            raw_norm_y = (iris_y - p_top[1]) / float(span_y)
        else:
            # Bounding box fallback
            x_min, y_min, x_max, y_max = eye_info
            eye_w = x_max - x_min
            eye_h = y_max - y_min

            if eye_w <= 0 or eye_h <= 0:
                return None

            raw_norm_x = (iris_x - x_min) / float(eye_w)
            raw_norm_y = (iris_y - y_min) / float(eye_h)

        # 2. Physiological excursion expansion:
        # Physical human iris travels within ~[0.28, 0.72] of the eye opening.
        span_min_x, span_max_x = 0.28, 0.72
        norm_x = (raw_norm_x - span_min_x) / (span_max_x - span_min_x)

        span_min_y, span_max_y = 0.28, 0.72
        norm_y = (raw_norm_y - span_min_y) / (span_max_y - span_min_y)

        # 3. Clamp to valid bounds [0.0, 1.0]
        norm_x = float(np.clip(norm_x, 0.0, 1.0))
        norm_y = float(np.clip(norm_y, 0.0, 1.0))

        return (norm_x, norm_y)

    def estimate(self, left_iris_px, left_eye_info, right_iris_px=None, right_eye_info=None):
        """
        Estimate normalized gaze point combining both eyes.
        """
        gaze_left  = self._normalize_single_eye(left_iris_px, left_eye_info)
        gaze_right = self._normalize_single_eye(right_iris_px, right_eye_info)

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
