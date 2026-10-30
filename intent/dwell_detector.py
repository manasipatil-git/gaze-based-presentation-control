# intent/dwell_detector.py
# ─────────────────────────────────────────────────────────────────────────────
# DwellDetector: Detects deliberate user intent via sustained gaze (dwell time).
#
# THE "MIDAS TOUCH" PROBLEM (College explanation):
#   In eye-tracking Human-Computer Interaction (HCI), eyes are primarily
#   sensory organs, not pointing devices. If every glance triggered a click,
#   the user would accidentally fire commands everywhere they look (the
#   mythological "Midas Touch" where everything touched turns to gold).
#
# HOW DWELL-BASED INTENT DETECTION WORKS:
#   1. Define target interaction zones at the left and right screen borders.
#   2. When calibrated gaze enters a zone:
#        -> Start a timer.
#   3. While gaze remains continuously inside that zone:
#        -> Calculate elapsed dwell time: (current_time - enter_time).
#   4. If elapsed dwell time >= DWELL_THRESHOLD (e.g. 1.8 seconds):
#        -> Fire the action EXACTLY ONCE (single-shot trigger).
#        -> Lock further triggers until the user looks away from the zone.
#   5. If gaze leaves the zone before threshold:
#        -> Reset the timer immediately (aborted glance, no false trigger).
# ─────────────────────────────────────────────────────────────────────────────

import time
from config import DWELL_TIME, ZONE_WIDTH_FRAC


class DwellDetector:
    """
    Monitors calibrated gaze coordinates to detect deliberate dwell within
    predefined left/right trigger zones.
    """

    def __init__(self, dwell_time: float = DWELL_TIME, zone_width_frac: float = ZONE_WIDTH_FRAC):
        """
        Parameters
        ----------
        dwell_time : float
            Required continuous gaze duration in seconds to trigger an action.
        zone_width_frac : float
            Fraction of the screen width allocated to left and right trigger zones.
        """
        self.dwell_time = dwell_time
        self.zone_width_frac = zone_width_frac

        # State tracking
        self.current_zone = None       # None, "LEFT", or "RIGHT"
        self.zone_enter_time = None    # Timestamp when current zone was entered
        self.has_triggered = False     # Prevents rapid multi-firing in the same dwell episode

        # Action display feedback
        self.last_action = None
        self.last_action_time = 0.0
        self.action_display_duration = 2.0  # Seconds to keep action notice visible

    def _determine_zone(self, calib_gaze):
        """
        Checks if the calibrated gaze (x, y in [0.0, 1.0]) lies in a trigger zone.
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

        Parameters
        ----------
        calib_gaze : tuple of (float, float) or None
            Calibrated screen gaze coordinates in [0.0, 1.0].

        Returns
        -------
        dict containing current intent, dwell duration, progress, and triggered action:
            {
                "zone": str or None ("LEFT", "RIGHT", or None),
                "intent_label": str ("PREV SLIDE", "NEXT SLIDE", or "NONE"),
                "dwell_duration": float (seconds),
                "dwell_threshold": float (seconds),
                "progress": float (0.0 to 1.0),
                "action_triggered": str or None ("PREV_SLIDE", "NEXT_SLIDE", or None),
                "active_action_banner": str or None
            }
        """
        now = time.time()
        detected_zone = self._determine_zone(calib_gaze)
        action_triggered = None

        if detected_zone is None:
            # Gaze is outside trigger zones -> Reset dwell timer
            self.current_zone = None
            self.zone_enter_time = None
            self.has_triggered = False
            dwell_duration = 0.0
        else:
            if detected_zone != self.current_zone:
                # Gaze just entered a new zone -> Start timer
                self.current_zone = detected_zone
                self.zone_enter_time = now
                self.has_triggered = False
                dwell_duration = 0.0
            else:
                # Gaze is continuing to dwell in the same zone
                dwell_duration = now - self.zone_enter_time

                # Check if dwell threshold is reached and hasn't fired yet
                if dwell_duration >= self.dwell_time and not self.has_triggered:
                    if self.current_zone == "LEFT":
                        action_triggered = "PREV_SLIDE"
                    elif self.current_zone == "RIGHT":
                        action_triggered = "NEXT_SLIDE"

                    self.has_triggered = True
                    self.last_action = action_triggered
                    self.last_action_time = now

                    print(f"\n[FocusLock Intent] >>> {action_triggered} TRIGGERED! (Dwell: {dwell_duration:.2f}s) <<<")

        # Compute progress ratio clamped to [0.0, 1.0]
        progress = min(1.0, dwell_duration / self.dwell_time) if self.current_zone else 0.0

        # Map zone to clean intent text for UI
        if self.current_zone == "LEFT":
            intent_label = "PREV SLIDE"
        elif self.current_zone == "RIGHT":
            intent_label = "NEXT SLIDE"
        else:
            intent_label = "NONE"

        # Check if recently triggered action should still be shown on UI
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
        self.has_triggered = False
