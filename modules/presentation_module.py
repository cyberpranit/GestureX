import time
import math
from modules.base_module import GestureModule

try:
    import pyautogui
except Exception:
    pass

class PresentationModule(GestureModule):
    def __init__(self, name, description, config_manager, ui_callback=None):
        super().__init__(name, description, config_manager)
        self.ui_callback = ui_callback # For laser pointer overlay (x, y)
        
        # Swipe tracking
        self.history = []
        self.history_len = 12
        self.last_swipe_time = 0.0
        self.swipe_cooldown = 1.0
        self.swipe_threshold = 0.15
        self.swipe_min_velocity = 0.4
        
        # Laser pointer smoothing
        self.prev_laser_x = 0
        self.prev_laser_y = 0
        self.smoothing = 0.6

    def on_enable(self):
        self.history = []
        self.last_swipe_time = 0.0
        self.prev_laser_x, self.prev_laser_y = pyautogui.position()

    def on_disable(self):
        # Clear laser pointer overlay when disabled
        if self.ui_callback:
            self.ui_callback(None, None)

    def process_hand_landmarks(self, hands_data, frame_size):
        if not hands_data:
            if self.ui_callback:
                self.ui_callback(None, None)
            return

        current_time = time.time()
        hand = hands_data[0]
        landmarks = hand['landmarks']

        # 1. Check if Open Palm is active (Laser Pointer Mode)
        is_palm = self.check_open_palm(landmarks)
        if is_palm:
            # Map index fingertip (landmark 8) to screen coordinates
            screen_w, screen_h = pyautogui.size()
            raw_x = 1.0 - landmarks[8][0] # Mirror coordinate
            raw_y = landmarks[8][1]
            
            # Map region centered around 0.25 to 0.75
            map_min, map_max = 0.25, 0.75
            mapped_x = max(0.0, min(1.0, (raw_x - map_min) / (map_max - map_min)))
            mapped_y = max(0.0, min(1.0, (raw_y - map_min) / (map_max - map_min)))
            
            target_x = int(mapped_x * screen_w)
            target_y = int(mapped_y * screen_h)
            
            # Smooth laser movement
            smooth_x = int(self.prev_laser_x * self.smoothing + target_x * (1.0 - self.smoothing))
            smooth_y = int(self.prev_laser_y * self.smoothing + target_y * (1.0 - self.smoothing))
            
            self.prev_laser_x = smooth_x
            self.prev_laser_y = smooth_y
            
            if self.ui_callback:
                self.ui_callback(smooth_x, smooth_y)
        else:
            if self.ui_callback:
                self.ui_callback(None, None)

        # 2. Check swipe history for slides navigation
        palm_x = 1.0 - landmarks[0][0]
        self.history.append((current_time, palm_x))
        if len(self.history) > self.history_len:
            self.history.pop(0)
            
        if len(self.history) >= 5 and (current_time - self.last_swipe_time) > self.swipe_cooldown:
            first_t, first_x = self.history[0]
            last_t, last_x = self.history[-1]
            
            dt = last_t - first_t
            dx = last_x - first_x
            
            if dt > 0.05 and dt < 0.6:
                velocity = abs(dx) / dt
                if abs(dx) > self.swipe_threshold and velocity > self.swipe_min_velocity:
                    if dx > 0:
                        # Swipe Right -> Next Slide
                        self.logger.info("Presentation: Swipe Right -> Next Slide")
                        pyautogui.press('right')
                        self.last_swipe_time = current_time
                        self.history.clear()
                    else:
                        # Swipe Left -> Previous Slide
                        self.logger.info("Presentation: Swipe Left -> Previous Slide")
                        pyautogui.press('left')
                        self.last_swipe_time = current_time
                        self.history.clear()

    def check_open_palm(self, landmarks):
        # Index, Middle, Ring, Pinky extended
        fingers_open = [
            landmarks[8][1] < landmarks[6][1],   # Index
            landmarks[12][1] < landmarks[10][1], # Middle
            landmarks[16][1] < landmarks[14][1], # Ring
            landmarks[20][1] < landmarks[18][1], # Pinky
        ]
        return all(fingers_open)
