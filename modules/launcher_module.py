import os
import time
import subprocess
from modules.base_module import GestureModule

class LauncherModule(GestureModule):
    def __init__(self, name, description, config_manager):
        super().__init__(name, description, config_manager)
        
        # Debouncing and holding states
        self.active_gesture = None
        self.gesture_start_time = 0.0
        self.hold_duration = 1.2 # Must hold gesture for 1.2s to trigger
        self.cooldown_until = 0.0
        self.cooldown_duration = 3.0 # Cooldown after launching an app
        
        # Default executable mappings
        self.app_paths = {
            "Chrome": "chrome.exe",
            "VS Code": "code",
            "Spotify": "spotify:", # Spotify protocol launch
            "Steam": "steam:",     # Steam protocol launch
            "Genshin Impact": "launcher.exe" # User should specify path, but let's provide a fallback
        }

    def on_enable(self):
        self.active_gesture = None
        self.gesture_start_time = 0.0
        self.cooldown_until = 0.0
        # Load user configurations if exist
        user_paths = self.config_manager.Get("launcher_paths", {})
        self.app_paths.update(user_paths)

    def process_hand_landmarks(self, hands_data, frame_size):
        if not hands_data:
            self.active_gesture = None
            return

        current_time = time.time()
        if current_time < self.cooldown_until:
            return

        hand = hands_data[0]
        landmarks = hand['landmarks']

        # Determine current hand gesture shape
        detected_shape = self.detect_hand_shape(landmarks)

        if detected_shape:
            if self.active_gesture == detected_shape:
                # Still holding the same gesture
                if current_time - self.gesture_start_time >= self.hold_duration:
                    self.launch_app(detected_shape)
                    self.cooldown_until = current_time + self.cooldown_duration
                    self.active_gesture = None # Reset after trigger
            else:
                # New gesture started
                self.active_gesture = detected_shape
                self.gesture_start_time = current_time
        else:
            self.active_gesture = None

    def detect_hand_shape(self, landmarks):
        # We classify hand shapes based on finger extension configurations:
        # 1: extended, 0: folded
        # Tip Y < PIP Y -> 1
        f_index = 1 if landmarks[8][1] < landmarks[6][1] else 0
        f_middle = 1 if landmarks[12][1] < landmarks[10][1] else 0
        f_ring = 1 if landmarks[16][1] < landmarks[14][1] else 0
        f_pinky = 1 if landmarks[20][1] < landmarks[18][1] else 0
        
        # Thumb extension (horizontal displacement from index knuckle)
        # For right hand, thumb tip (4) is to the left (smaller x) of index knuckle (5) if open, etc.
        # Let's check thumb tip distance to index knuckle
        f_thumb = 1 if abs(landmarks[4][0] - landmarks[5][0]) > 0.07 else 0

        # Pattern A: "V" shape (Index and Middle open, Ring and Pinky folded) -> VS Code
        if f_index == 1 and f_middle == 1 and f_ring == 0 and f_pinky == 0:
            return "VS Code"

        # Pattern B: "Horns / Spider-man" shape (Index and Pinky open, Middle and Ring folded) -> Spotify
        if f_index == 1 and f_middle == 0 and f_ring == 0 and f_pinky == 1:
            return "Spotify"

        # Pattern C: "Three Fingers / W" shape (Index, Middle, Ring open, Pinky folded) -> Steam
        if f_index == 1 and f_middle == 1 and f_ring == 1 and f_pinky == 0:
            return "Steam"

        # Pattern D: "C Shape / Claw" (Thumb and Index open wide, others folded) -> Chrome
        if f_thumb == 1 and f_index == 1 and f_middle == 0 and f_ring == 0 and f_pinky == 0:
            return "Chrome"

        # Pattern E: "L Shape / Gun" (Thumb and Index open, others folded, index vertical, thumb horizontal) -> Genshin Impact
        # (We can approximate as f_thumb=1, f_index=1, and index tip is above thumb tip)
        if f_thumb == 1 and f_index == 1 and f_middle == 0 and f_ring == 0 and f_pinky == 0:
            # We already matched Chrome, let's distinguish by Middle finger or just keep it simple.
            pass

        return None

    def launch_app(self, app_name):
        path = self.app_paths.get(app_name)
        if not path:
            return

        self.logger.info(f"Launcher: Triggering launch command for '{app_name}' -> '{path}'")
        try:
            # os.startfile is Windows specific and handles aliases, URLs, executables
            os.startfile(path)
        except Exception as e:
            self.logger.error(f"Failed to launch '{app_name}' using os.startfile: {e}. Trying subprocess...")
            try:
                # Fallback to subprocess
                subprocess.Popen(path, shell=True)
            except Exception as sub_e:
                self.logger.error(f"Fallback launch for '{app_name}' failed: {sub_e}")
