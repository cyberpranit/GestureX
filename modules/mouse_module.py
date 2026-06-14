import time
import math
from modules.base_module import GestureModule

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except Exception:
    pass

class MouseModule(GestureModule):
    def __init__(self, name, description, config_manager):
        super().__init__(name, description, config_manager)
        self.prev_x, self.prev_y = 0, 0
        self.smoothing = 0.7  # Higher = smoother but more lag
        self.click_threshold = 0.035
        self.is_left_clicked = False
        self.is_right_clicked = False
        
        # Scroll tracking
        self.prev_scroll_y = None
        self.scroll_threshold = 0.04
        
        # Speed multiplier
        self.mouse_speed = 1.5

    def on_enable(self):
        self.prev_x, self.prev_y = pyautogui.position()
        self.is_left_clicked = False
        self.is_right_clicked = False
        self.prev_scroll_y = None
        self.mouse_speed = self.config_manager.Get("air_mouse_speed", 1.5)

    def on_disable(self):
        # Ensure buttons are released when disabled
        if self.is_left_clicked:
            pyautogui.mouseUp(button='left')
        if self.is_right_clicked:
            pyautogui.mouseUp(button='right')

    def process_hand_landmarks(self, hands_data, frame_size):
        # Air mouse targets the Right hand
        right_hand = None
        for hand in hands_data:
            if hand['handedness'] == 'Right':
                right_hand = hand
                break

        if not right_hand:
            # If hand is lost, make sure we release any held clicks
            if self.is_left_clicked:
                pyautogui.mouseUp(button='left')
                self.is_left_clicked = False
            return

        landmarks = right_hand['landmarks']
        screen_w, screen_h = pyautogui.size()
        
        # 1. Finger extensions checks
        # Index open, Middle open, others closed
        index_open = landmarks[8][1] < landmarks[6][1]
        middle_open = landmarks[12][1] < landmarks[10][1]
        ring_open = landmarks[16][1] < landmarks[14][1]
        pinky_open = landmarks[20][1] < landmarks[18][1]
        
        # Pinch distances
        # Thumb (4) to Index (8)
        d_thumb_index = math.sqrt((landmarks[4][0] - landmarks[8][0])**2 + (landmarks[4][1] - landmarks[8][1])**2)
        # Thumb (4) to Middle (12)
        d_thumb_middle = math.sqrt((landmarks[4][0] - landmarks[12][0])**2 + (landmarks[4][1] - landmarks[12][1])**2)

        # Mode A: Scroll Mode (Index + Middle extended, ring + pinky closed)
        if index_open and middle_open and not ring_open and not pinky_open:
            # Release click if we were clicking
            if self.is_left_clicked:
                pyautogui.mouseUp(button='left')
                self.is_left_clicked = False
            
            curr_y = landmarks[8][1]  # Track index tip Y
            if self.prev_scroll_y is not None:
                dy = curr_y - self.prev_scroll_y
                # If vertical displacement exceeds threshold, scroll
                if abs(dy) > 0.01:
                    scroll_amount = int(-dy * 1500) # Negative because Y points down
                    pyautogui.scroll(scroll_amount)
            self.prev_scroll_y = curr_y
            return
            
        # Reset scroll tracking if not in scroll mode
        self.prev_scroll_y = None

        # Mode B: Left Click / Drag (Thumb-Index Pinch)
        if d_thumb_index < self.click_threshold:
            if not self.is_left_clicked:
                pyautogui.mouseDown(button='left')
                self.is_left_clicked = True
                self.logger.debug("Air Mouse: Left click down")
        else:
            if self.is_left_clicked:
                pyautogui.mouseUp(button='left')
                self.is_left_clicked = False
                self.logger.debug("Air Mouse: Left click up")

        # Mode C: Right Click (Thumb-Middle Pinch)
        if d_thumb_middle < self.click_threshold:
            if not self.is_right_clicked:
                pyautogui.mouseDown(button='right')
                self.is_right_clicked = True
                self.logger.debug("Air Mouse: Right click down")
        else:
            if self.is_right_clicked:
                pyautogui.mouseUp(button='right')
                self.is_right_clicked = False
                self.logger.debug("Air Mouse: Right click up")

        # Mode D: Cursor Movement (Index extended or default tracking)
        # We use index tip (8) or MCP (5) for movement tracking. Let's use index tip (8) for drawing, 
        # or MCP (5) for standard cursor since it's more stable. Let's use Index tip (8).
        # Mirror: X from camera is inverted. Natural movement: X = 1.0 - x_landmark
        raw_x = 1.0 - landmarks[8][0]
        raw_y = landmarks[8][1]

        # Apply speed multiplier and map to screen dimensions.
        # We can center the mapping range (e.g. index coordinates between 0.2 and 0.8) to make it easier to reach screen edges.
        map_min, map_max = 0.25, 0.75
        mapped_x = (raw_x - map_min) / (map_max - map_min)
        mapped_y = (raw_y - map_min) / (map_max - map_min)
        
        # Clamp mapped values
        mapped_x = max(0.0, min(1.0, mapped_x))
        mapped_y = max(0.0, min(1.0, mapped_y))
        
        target_x = int(mapped_x * screen_w)
        target_y = int(mapped_y * screen_h)

        # Smooth position
        smooth_x = int(self.prev_x * self.smoothing + target_x * (1.0 - self.smoothing))
        smooth_y = int(self.prev_y * self.smoothing + target_y * (1.0 - self.smoothing))

        pyautogui.moveTo(smooth_x, smooth_y)
        
        self.prev_x = smooth_x
        self.prev_y = smooth_y
