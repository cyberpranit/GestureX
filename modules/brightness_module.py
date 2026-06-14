import math
from modules.base_module import GestureModule
from utils.sys_utils import SetSystemBrightness, GetSystemBrightness

class BrightnessModule(GestureModule):
    def __init__(self, name, description, config_manager, ui_callback=None):
        super().__init__(name, description, config_manager)
        self.ui_callback = ui_callback
        self.last_brightness = -1
        self.smoothing_list = []
        self.smoothing_factor = 5 # Number of frames to average

    def on_enable(self):
        self.last_brightness = GetSystemBrightness()
        self.smoothing_list = []

    def process_hand_landmarks(self, hands_data, frame_size):
        # Target Right hand only
        right_hand = None
        for hand in hands_data:
            if hand['handedness'] == 'Right':
                right_hand = hand
                break
                
        if not right_hand:
            return

        landmarks = right_hand['landmarks']
        # Landmark index 4: Thumb Tip, 8: Index Tip
        p4 = landmarks[4]
        p8 = landmarks[8]

        # Calculate Euclidean distance in 2D (x, y)
        dx = p4[0] - p8[0]
        dy = p4[1] - p8[1]
        dist = math.sqrt(dx*dx + dy*dy)

        # Standard range calibration: min~0.02, max~0.20
        min_dist = 0.02
        max_dist = 0.18

        # Clamp distance and map linearly to 0 - 100
        dist_clamped = max(min_dist, min(max_dist, dist))
        raw_val = (dist_clamped - min_dist) / (max_dist - min_dist)
        target_brightness = int(raw_val * 100)

        # Apply moving average smoothing
        self.smoothing_list.append(target_brightness)
        if len(self.smoothing_list) > self.smoothing_factor:
            self.smoothing_list.pop(0)
        smoothed_brightness = int(sum(self.smoothing_list) / len(self.smoothing_list))

        # Apply hysteresis: only change if difference >= 3% to avoid CPU strain on brightness API
        if self.last_brightness == -1 or abs(smoothed_brightness - self.last_brightness) >= 3 or smoothed_brightness == 0 or smoothed_brightness == 100:
            self.last_brightness = smoothed_brightness
            SetSystemBrightness(smoothed_brightness)
            
            # Fire UI callback for overlays
            if self.ui_callback:
                self.ui_callback(smoothed_brightness)
