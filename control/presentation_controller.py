# control/presentation_controller.py
# ─────────────────────────────────────────────────────────────────────────────
# PresentationController: Bridges detected gaze intent to OS keyboard commands.
#
# HOW IT WORKS (College explanation):
#   1. When DwellDetector confirms an intent ('NEXT_SLIDE' or 'PREV_SLIDE'),
#      this controller acts as the actuation layer.
#   2. In standard presentation software (PowerPoint, Google Slides, Keynote,
#      PDF viewers), pressing the RIGHT arrow key advances to the next slide,
#      and the LEFT arrow key returns to the previous slide.
#   3. PyAutoGUI synthesizes real OS-level keyboard events to trigger slide changes.
#
# SAFETY - DEMO_MODE:
#   During live presentations or evaluation, accidental keypresses could switch
#   slides prematurely or interfere with other open windows.
#   - DEMO_MODE = True  -> Logs & displays the triggered action safely without
#                          sending real keyboard events.
#   - DEMO_MODE = False -> Sends actual 'right' and 'left' keypresses to the OS.
# ─────────────────────────────────────────────────────────────────────────────

import pyautogui
from config import DEMO_MODE

# Configure PyAutoGUI safety parameters
pyautogui.FAILSAFE = True   # Moving mouse to screen corner aborts automation
pyautogui.PAUSE = 0.05      # Minimal delay after each keypress


class PresentationController:
    """
    Translates intent commands into OS keyboard actions using PyAutoGUI.
    """

    def __init__(self, demo_mode: bool = DEMO_MODE):
        """
        Parameters
        ----------
        demo_mode : bool
            If True, simulates actions without sending actual keyboard events.
        """
        self.demo_mode = demo_mode
        self.action_history = []
        self.last_action = None

    def trigger_action(self, action: str):
        """
        Executes or simulates the keyboard command corresponding to the intent action.

        Parameters
        ----------
        action : str
            "NEXT_SLIDE" or "PREV_SLIDE"

        Returns
        -------
        dict with status details:
            {
                "action": str,
                "key": str,
                "executed": bool,
                "demo_mode": bool,
                "message": str
            }
        """
        if not action:
            return None

        key_to_press = None
        description = ""

        if action == "NEXT_SLIDE":
            key_to_press = "right"
            description = "NEXT SLIDE (Right Arrow)"
        elif action == "PREV_SLIDE":
            key_to_press = "left"
            description = "PREVIOUS SLIDE (Left Arrow)"
        else:
            print(f"[FocusLock Controller] Unknown action: {action}")
            return None

        # Execute or simulate
        if self.demo_mode:
            message = f"[DEMO MODE] {description} Simulated (No real keypress)"
            executed = False
            print(f"\n{message}")
        else:
            try:
                pyautogui.press(key_to_press)
                message = f"[LIVE MODE] {description} Dispatched to OS!"
                executed = True
                print(f"\n{message}")
            except Exception as e:
                message = f"[ERROR] Failed to send keypress: {e}"
                executed = False
                print(f"\n{message}")

        result = {
            "action": action,
            "key": key_to_press,
            "executed": executed,
            "demo_mode": self.demo_mode,
            "message": message
        }

        self.last_action = result
        self.action_history.append(result)
        return result

    def toggle_demo_mode(self):
        """
        Toggle between DEMO_MODE and LIVE_MODE at runtime.
        Returns the new boolean state of demo_mode.
        """
        self.demo_mode = not self.demo_mode
        mode_label = "DEMO MODE (Safe Simulation)" if self.demo_mode else "LIVE MODE (Sending Keypresses!)"
        print(f"\n[FocusLock Controller] Switched to: {mode_label}")
        return self.demo_mode
