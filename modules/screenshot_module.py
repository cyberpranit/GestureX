import os
import time
from datetime import datetime
from modules.base_module import GestureModule

# We will import QApplication from PyQt6 when needed or use a callback
# Since this module is run within the PyQt6 application loop, we can use QApplication
from PyQt6.QtWidgets import QApplication

class ScreenshotModule(GestureModule):
    def __init__(self, name, description, config_manager, ui_callback=None):
        super().__init__(name, description, config_manager)
        self.ui_callback = ui_callback
        
        # State machine for gesture transition: Open Palm -> Closed Fist
        self.state = "NONE" # NONE, PALM_DETECTED
        self.palm_detected_time = 0.0
        self.cooldown_time = 0.0
        
        # Thresholds
        self.transition_window = 1.2 # Must fist within 1.2s of palm
        self.gesture_cooldown = 2.0  # Cooldown between screenshots

    def on_enable(self):
        self.state = "NONE"
        self.palm_detected_time = 0.0
        self.cooldown_time = 0.0

    def process_hand_landmarks(self, hands_data, frame_size):
        # We need at least one hand
        if not hands_data:
            return

        current_time = time.time()
        if current_time < self.cooldown_time:
            return

        # Check the first available hand
        hand = hands_data[0]
        landmarks = hand['landmarks']

        # Determine if hand is Open Palm or Closed Fist
        is_palm = self.check_open_palm(landmarks)
        is_fist = self.check_closed_fist(landmarks)

        if self.state == "NONE":
            if is_palm:
                self.state = "PALM_DETECTED"
                self.palm_detected_time = current_time
                self.logger.debug("Screenshot Gesture: Open Palm detected. Waiting for Closed Fist...")
        elif self.state == "PALM_DETECTED":
            # Check timeout
            if current_time - self.palm_detected_time > self.transition_window:
                self.state = "NONE"
                self.logger.debug("Screenshot Gesture: Timeout waiting for Closed Fist.")
            elif is_fist:
                # Triger screenshot!
                self.state = "NONE"
                self.cooldown_time = current_time + self.gesture_cooldown
                self.logger.info("Screenshot Gesture: Palm -> Fist sequence complete. Capturing screen...")
                self.take_screenshot()

    def check_open_palm(self, landmarks):
        # Check if index (8), middle (12), ring (16), and pinky (20) tips are higher than PIP joints
        # (MediaPipe Y decreases going up, so tip Y < PIP Y)
        fingers_open = [
            landmarks[8][1] < landmarks[6][1],   # Index
            landmarks[12][1] < landmarks[10][1], # Middle
            landmarks[16][1] < landmarks[14][1], # Ring
            landmarks[20][1] < landmarks[18][1], # Pinky
        ]
        # For palm, all four fingers must be open
        return all(fingers_open)

    def check_closed_fist(self, landmarks):
        # For fist, all four fingers must be closed (tip Y > PIP Y)
        fingers_closed = [
            landmarks[8][1] > landmarks[6][1],   # Index
            landmarks[12][1] > landmarks[10][1], # Middle
            landmarks[16][1] > landmarks[14][1], # Ring
            landmarks[20][1] > landmarks[18][1], # Pinky
        ]
        return all(fingers_closed)

    def take_screenshot(self):
        try:
            # Create screenshot directories
            from utils.paths import get_screenshot_dir
            base_folder = self.config_manager.Get("screenshot_folder", "screenshots")
            base_folder = get_screenshot_dir(base_folder)
                
            today_str = datetime.now().strftime("%Y-%m-%d")
            folder_path = os.path.join(base_folder, today_str)
            os.makedirs(folder_path, exist_ok=True)

            timestamp_str = datetime.now().strftime("%H-%M-%S")
            file_name = f"{timestamp_str}.png"
            full_path = os.path.join(folder_path, file_name)

            # Perform PyQt screen grab
            app = QApplication.instance()
            if app:
                # Need to grab on primary screen on main thread safely, 
                # but since screenshots are triggered by the logic loop on main thread, it is safe.
                screen = app.primaryScreen()
                if screen:
                    pixmap = screen.grabWindow(0)
                    pixmap.save(full_path, "PNG")
                    self.logger.info(f"Screenshot saved to: {full_path}")
                    
                    if self.ui_callback:
                        self.ui_callback(full_path)
                    return
            
            # Fallback to pyautogui if QApplication screen grab is unavailable
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save(full_path)
            self.logger.info(f"Screenshot captured via pyautogui: {full_path}")
            
            if self.ui_callback:
                self.ui_callback(full_path)
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
