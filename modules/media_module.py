import time
from modules.base_module import GestureModule

try:
    import pyautogui
except Exception:
    pass

class MediaModule(GestureModule):
    def __init__(self, name, description, config_manager):
        super().__init__(name, description, config_manager)
        self.history = [] # List of tuples: (timestamp, x_coord)
        self.history_len = 15
        
        # Gestures state tracking
        self.last_gesture_time = 0.0
        self.cooldown = 1.2 # Cooldown in seconds between media actions
        
        # Swipe thresholds
        self.swipe_threshold = 0.15 # Minimum movement in normalized width
        self.swipe_min_velocity = 0.4 # Minimum speed
        
        # Thumb up debounce
        self.thumb_up_active = False

    def on_enable(self):
        self.history = []
        self.last_gesture_time = 0.0
        self.thumb_up_active = False

    def process_hand_landmarks(self, hands_data, frame_size):
        if not hands_data:
            return

        current_time = time.time()
        hand = hands_data[0]
        landmarks = hand['landmarks']

        # Get palm x coordinate (landmark 0 - Wrist)
        # Mirror x-axis: 1.0 - raw_x to match physical right/left movement
        palm_x = 1.0 - landmarks[0][0]
        
        # Add to history
        self.history.append((current_time, palm_x))
        if len(self.history) > self.history_len:
            self.history.pop(0)

        # 1. Check for Swipes (Swipe Right = Next Track, Swipe Left = Prev Track)
        if len(self.history) >= 5 and (current_time - self.last_gesture_time) > self.cooldown:
            first_t, first_x = self.history[0]
            last_t, last_x = self.history[-1]
            
            dt = last_t - first_t
            dx = last_x - first_x
            
            if dt > 0.05 and dt < 0.6: # Swipe time window
                velocity = abs(dx) / dt
                if abs(dx) > self.swipe_threshold and velocity > self.swipe_min_velocity:
                    if dx > 0:
                        # Swipe Right -> Next Track
                        self.logger.info("Media Gesture: Swipe Right -> Next Track")
                        pyautogui.press('nexttrack')
                        self.last_gesture_time = current_time
                        self.history.clear()
                        return
                    else:
                        # Swipe Left -> Previous Track
                        self.logger.info("Media Gesture: Swipe Left -> Previous Track")
                        pyautogui.press('prevtrack')
                        self.last_gesture_time = current_time
                        self.history.clear()
                        return

        # 2. Check for Thumb Up (Play/Pause)
        is_thumb_up = self.check_thumb_up(landmarks)
        if is_thumb_up:
            if not self.thumb_up_active and (current_time - self.last_gesture_time) > self.cooldown:
                self.logger.info("Media Gesture: Thumb Up -> Play/Pause")
                pyautogui.press('playpause')
                self.last_gesture_time = current_time
                self.thumb_up_active = True
        else:
            self.thumb_up_active = False

    def check_thumb_up(self, landmarks):
        # Thumb tip (4) should be higher than thumb IP (3) and MCP (2)
        # Higher means lower Y value in MediaPipe
        thumb_is_up = landmarks[4][1] < landmarks[3][1] and landmarks[3][1] < landmarks[2][1]
        
        # Other fingers (8, 12, 16, 20) should be folded
        # Folded means their tip Y is greater than their PIP Y
        fingers_folded = [
            landmarks[8][1] > landmarks[6][1],   # Index
            landmarks[12][1] > landmarks[10][1], # Middle
            landmarks[16][1] > landmarks[14][1], # Ring
            landmarks[20][1] > landmarks[18][1], # Pinky
        ]
        
        # Also, check that the thumb is not pointed sideways too much
        # For a clean thumb up, we want the thumb tip to be significantly higher than the wrist
        thumb_higher_than_wrist = landmarks[4][1] < landmarks[0][1] - 0.1
        
        return thumb_is_up and all(fingers_folded) and thumb_higher_than_wrist
