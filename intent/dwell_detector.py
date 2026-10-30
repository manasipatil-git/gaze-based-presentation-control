# intent/dwell_detector.py
# ─────────────────────────────────────────────────────────────────────────────
# DwellDetector: Detects deliberate user intent via sustained gaze (dwell time).
#
# GRACE PERIOD / HYSTERESIS (Fixes "partially triggering" & jitter):
#   In real webcam usage, holding gaze at the screen edge involves natural
#   micro-saccades and involuntary blinks. If a single camera frame drops or
#   the gaze briefly flickers 1 pixel outside the zone, an unbuffered system
#   instantly zeroes the dwell timer, frustrating the user.
#
#   DwellDetector implements a 0.35s Grace Period:
#     - If gaze momentarily slips out of the zone and returns within 0.35s,
#       the dwell timer DOES NOT reset.
#     - Only if the user genuinely looks away for > 0.35s is the timer reset.
#
# SINGLE-SHOT ACTION LOCK:
#   Once DWELL_TIME (1.2s) is reached, the action fires EXACTLY ONCE.
#   It remains locked until the user returns their gaze toward center.
# ─────────────────────────────────────────────────────────────────────────────

import time
from config import DWELL_TIME, ZONE_WIDTH_FRAC, DWELL_GRACE_PERIOD


class DwellDetector:
    """
    Monitors calibrated gaze coordinates to detect deliberate dwell within
    predefined left/right trigger zones, with blink and jitter grace tolerance.
    """

    def __init__(self, dwell_time: float = DWELL_TIME,
                 zone_width_frac: float = ZONE_WIDTH_FRAC,
                 grace_period: float = DWELL_GRACE_PERIOD):
        """
        Parameters
        ----------
        dwell_time : float
            Continuous gaze duration (seconds) required to trigger an action.
        zone_width_frac : float
            Fraction of the screen width allocated to left and right trigger zones.
        grace_period : float
            Seconds of tolerance allowing momentary blinks/jitter without resetting dwell.
        """
        self.dwell_time = dwell_time
        self.zone_width_frac = zone_width_frac
        self.grace_period = grace_period

        # State tracking
        self.current_zone = None          # None, "LEFT", or "RIGHT"
        self.zone_enter_time = None       # Timestamp when current zone was entered
        self.last_in_zone_time = None     # Timestamp when gaze was last confirmed in zone
        self.has_triggered = False        # Single-shot trigger protection

        # Action display feedback
        self.last_action = None
        self.last_action_time = 0.0
        self.action_display_duration = 2.0  # Seconds to keep action notice visible

    def _determine_zone(self, calib_gaze):
        """
        Checks if the calibrated gaze (x in [0.0, 1.0]) lies in a trigger zone.
        """
        if calib_gaze is None:
            return None

        gx, _ = calib_gaze
        if gx <= self.zone_width_frac:
            return "LEFT"
        elif gx >= (1.0 - self.zone_width_frac):
            return "RIGHT"
        return None

    def update(self, calib_gaze):
        """
        Update the dwell state machine with the latest calibrated gaze position.
        """
        now = time.time()
        detected_zone = self._determine_zone(calib_gaze)
        action_triggered = None
        dwell_duration = 0.0

        if detected_zone is not None:
            # Gaze is currently inside a trigger zone
            if detected_zone != self.current_zone:
                # Switched to a new zone
                self.current_zone = detected_zone
                self.zone_enter_time = now
                self.last_in_zone_time = now
                self.has_triggered = False
                dwell_duration = 0.0
            else:
                # Continuing to dwell in the same zone
                self.last_in_zone_time = now
                dwell_duration = now - self.zone_enter_time

                # Check if threshold reached
                if dwell_duration >= self.dwell_time and not self.has_triggered:
                    if self.current_zone == "LEFT":
                        action_triggered = "PREV_SLIDE"
                    elif self.current_zone == "RIGHT":
                        action_triggered = "NEXT_SLIDE"

                    self.has_triggered = True
                    self.last_action = action_triggered
                    self.last_action_time = now
                    print(f"\n[FocusLock Intent] >>> {action_triggered} TRIGGERED! (Dwell: {dwell_duration:.2f}s) <<<")
        else:
            # Gaze is temporarily or permanently outside trigger zones
            if self.current_zone is not None and self.last_in_zone_time is not None:
                time_outside = now - self.last_in_zone_time

                if time_outside <= self.grace_period and not self.has_triggered:
                    # Within grace period: preserve dwell timer across the brief blink/jitter!
                    dwell_duration = self.last_in_zone_time - self.zone_enter_time
                else:
                    # Grace period expired: genuine glance away toward center
                    self.current_zone = None
                    self.zone_enter_time = None
                    self.last_in_zone_time = None
                    self.has_triggered = False
                    dwell_duration = 0.0
            else:
                self.current_zone = None
                self.zone_enter_time = None
                self.has_triggered = False
                dwell_duration = 0.0

        # Compute progress ratio clamped to [0.0, 1.0]
        progress = min(1.0, dwell_duration / self.dwell_time) if self.current_zone else 0.0

        # UI intent label
        if self.current_zone == "LEFT":
            intent_label = "PREV SLIDE"
        elif self.current_zone == "RIGHT":
            intent_label = "NEXT SLIDE"
        else:
            intent_label = "NONE"

        # Action notification banner
        active_action_banner = None
        if self.last_action and (now - self.last_action_time <= self.action_display_duration):
            active_action_banner = self.last_action

        return {
            "zone": self.current_zone,
            "intent_label": intent_label,
            "dwell_duration": dwell_duration,
            "dwell_threshold": self.dwell_time,
            "progress": progress,
            "has_triggered": self.has_triggered,
            "action_triggered": action_triggered,
            "active_action_banner": active_action_banner
        }

    def reset(self):
        """Reset internal dwell state."""
        self.current_zone = None
        self.zone_enter_time = None
        self.last_in_zone_time = None
        self.has_triggered = False
