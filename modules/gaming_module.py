import time
from modules.base_module import GestureModule
from utils.sys_utils import SetMicrophoneMute

try:
    import pyautogui
except Exception:
    pass

class GamingModule(GestureModule):
    def __init__(self, name, description, config_manager, ui_callback=None):
        super().__init__(name, description, config_manager)
        self.ui_callback = ui_callback
        
        # Debounce
        self.last_obs_time = 0.0
        self.last_mic_time = 0.0
        self.action_cooldown = 2.0
        
        # Mic mute state
        self.mic_muted = False
        
        # Gestures state tracker
        self.obs_active = False
        self.mic_active = False

    def on_enable(self):
        self.last_obs_time = 0.0
        self.last_mic_time = 0.0
        self.mic_muted = False
        self.obs_active = False
        self.mic_active = False

    def process_hand_landmarks(self, hands_data, frame_size):
        if not hands_data:
            return

        current_time = time.time()
        hand = hands_data[0]
        landmarks = hand['landmarks']

        # 1. Check for "Three Fingers Up" -> Toggle OBS Recording (default hotkey Ctrl+Shift+R)
        is_three_fingers = self.check_three_fingers_up(landmarks)
        if is_three_fingers:
            if not self.obs_active and (current_time - self.last_obs_time) > self.action_cooldown:
                self.logger.info("Gaming Gesture: Three Fingers -> Toggling OBS Recording")
                # Simulate OBS recording toggle hotkey
                pyautogui.hotkey('ctrl', 'shift', 'r')
                self.last_obs_time = current_time
                self.obs_active = True
                if self.ui_callback:
                    self.ui_callback("OBS Recording Toggled")
        else:
            self.obs_active = False

        # 2. Check for "Shaka" gesture (Thumb & Pinky extended, middle three folded) -> Toggle Mic Mute
        is_shaka = self.check_shaka_gesture(landmarks)
        if is_shaka:
            if not self.mic_active and (current_time - self.last_mic_time) > self.action_cooldown:
                self.mic_muted = not self.mic_muted
                self.logger.info(f"Gaming Gesture: Shaka -> Setting Microphone Mute: {self.mic_muted}")
                SetMicrophoneMute(self.mic_muted)
                
                # Also optionally send hotkey for Discord Mute (default Ctrl+Shift+M)
                pyautogui.hotkey('ctrl', 'shift', 'm')
                
                self.last_mic_time = current_time
                self.mic_active = True
                if self.ui_callback:
                    self.ui_callback(f"Microphone: {'MUTED' if self.mic_muted else 'ACTIVE'}")
        else:
            self.mic_active = False

    def check_three_fingers_up(self, landmarks):
        # Index, Middle, Ring extended
        # Pinky folded
        f_index = landmarks[8][1] < landmarks[6][1]
        f_middle = landmarks[12][1] < landmarks[10][1]
        f_ring = landmarks[16][1] < landmarks[14][1]
        f_pinky = landmarks[20][1] > landmarks[18][1]
        
        return f_index and f_middle and f_ring and f_pinky

    def check_shaka_gesture(self, landmarks):
        # Thumb extended, Pinky extended
        # Index, Middle, Ring folded
        f_thumb = abs(landmarks[4][0] - landmarks[5][0]) > 0.08
        f_index = landmarks[8][1] > landmarks[6][1]
        f_middle = landmarks[12][1] > landmarks[10][1]
        f_ring = landmarks[16][1] > landmarks[14][1]
        f_pinky = landmarks[20][1] < landmarks[18][1]
        
        return f_thumb and f_index and f_middle and f_ring and f_pinky
