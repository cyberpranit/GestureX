import os
import time
from datetime import datetime
from modules.base_module import GestureModule
from utils.sys_utils import LockPC, SetMicrophoneMute

class SecurityModule(GestureModule):
    def __init__(self, name, description, config_manager, ui_callback=None):
        super().__init__(name, description, config_manager)
        self.ui_callback = ui_callback # For blurring screen and alerts
        
        # Lock PC state
        self.last_lock_time = 0.0
        self.lock_cooldown = 5.0
        
        # Privacy Mode state
        self.privacy_mode_active = False
        self.privacy_hold_start = 0.0
        self.privacy_holding = False
        self.privacy_hold_duration = 3.0 # Hold for 3s
        
        # Face landmarks for registration (owner ratios)
        self.owner_face_ratio = None
        self.last_face_check_time = 0.0
        self.face_check_cooldown = 3.0 # Check face every 3 seconds

    def on_enable(self):
        self.last_lock_time = 0.0
        self.privacy_mode_active = False
        self.privacy_holding = False
        self.privacy_hold_start = 0.0
        # Load owner face ratio if saved
        self.owner_face_ratio = self.config_manager.Get("owner_face_ratio", None)

    def on_disable(self):
        if self.privacy_mode_active:
            self.toggle_privacy_mode(False)

    def process_hand_landmarks(self, hands_data, frame_size):
        current_time = time.time()
        
        # 1. Lock PC: Detect if BOTH hands are present and BOTH are Open Palms
        if len(hands_data) >= 2 and (current_time - self.last_lock_time) > self.lock_cooldown:
            hand_1_palm = self.check_open_palm(hands_data[0]['landmarks'])
            hand_2_palm = self.check_open_palm(hands_data[1]['landmarks'])
            if hand_1_palm and hand_2_palm:
                self.logger.info("Security Gesture: Both Palms Raised -> Locking Workstation")
                self.last_lock_time = current_time
                LockPC()
                return

        # 2. Privacy Mode: Check if five fingers of ONE hand are held up for 3 seconds
        if len(hands_data) == 1:
            hand = hands_data[0]
            is_five_fingers = self.check_five_fingers_open(hand['landmarks'])
            if is_five_fingers:
                if not self.privacy_holding:
                    self.privacy_holding = True
                    self.privacy_hold_start = current_time
                    self.logger.debug("Security: Five fingers held. Initiating Privacy countdown (3s)...")
                else:
                    if current_time - self.privacy_hold_start >= self.privacy_hold_duration:
                        # Toggle Privacy Mode!
                        self.privacy_mode_active = not self.privacy_mode_active
                        self.toggle_privacy_mode(self.privacy_mode_active)
                        self.privacy_holding = False # Reset hold
            else:
                self.privacy_holding = False
        else:
            self.privacy_holding = False

    def check_open_palm(self, landmarks):
        fingers_open = [
            landmarks[8][1] < landmarks[6][1],
            landmarks[12][1] < landmarks[10][1],
            landmarks[16][1] < landmarks[14][1],
            landmarks[20][1] < landmarks[18][1],
        ]
        return all(fingers_open)

    def check_five_fingers_open(self, landmarks):
        # Index, Middle, Ring, Pinky extended
        fingers_open = [
            landmarks[8][1] < landmarks[6][1],
            landmarks[12][1] < landmarks[10][1],
            landmarks[16][1] < landmarks[14][1],
            landmarks[20][1] < landmarks[18][1],
        ]
        # Thumb extended (horizontal gap from index base)
        thumb_open = abs(landmarks[4][0] - landmarks[5][0]) > 0.08
        return all(fingers_open) and thumb_open

    def toggle_privacy_mode(self, activate=True):
        self.logger.info(f"Security: Toggling Privacy Mode to: {activate}")
        
        # Hardware Microphone Mute
        SetMicrophoneMute(activate)
        
        # Notify UI to show Blur Overlay
        if self.ui_callback:
            self.ui_callback("PRIVACY_BLUR", activate)

    # 3. Face processing called by Core camera loop to detect intruders
    def process_face_landmarks(self, face_landmarks, frame, frame_size):
        """
        Processes face landmarks to verify the user identity.
        Called directly from ModuleManager when CameraThread emits a face.
        """
        current_time = time.time()
        if current_time - self.last_face_check_time < self.face_check_cooldown:
            return

        self.last_face_check_time = current_time

        if not face_landmarks:
            return

        # Simple feature ratio check:
        # Distance between eyes vs face height
        # Left eye (landmark 33), Right eye (landmark 263), Top head (landmark 10), Chin (landmark 152)
        try:
            # MediaPipe FaceMesh Landmark Index mappings
            # Let's extract approximate screen positions
            # In normalized coordinates
            pt_le = face_landmarks[33]
            pt_re = face_landmarks[263]
            pt_top = face_landmarks[10]
            pt_chin = face_landmarks[152]
            
            eye_dist = ((pt_le[0] - pt_re[0])**2 + (pt_le[1] - pt_re[1])**2)**0.5
            face_height = ((pt_top[0] - pt_chin[0])**2 + (pt_top[1] - pt_chin[1])**2)**0.5
            
            if face_height == 0:
                return
                
            current_ratio = eye_dist / face_height
            
            if self.owner_face_ratio is None:
                # First time face registration: Save owner profile ratio
                self.owner_face_ratio = current_ratio
                self.config_manager.Set("owner_face_ratio", current_ratio)
                self.logger.info(f"Registered owner face ratio: {current_ratio:.4f}")
                if self.ui_callback:
                    self.ui_callback("FACE_REGISTERED", f"Ratio: {current_ratio:.4f}")
            else:
                # Compare ratio
                diff = abs(current_ratio - self.owner_face_ratio)
                # If variance exceeds 18%, we treat it as an unknown intruder face!
                if diff > 0.05:
                    self.logger.warning(f"Intruder detected! Face ratio difference: {diff:.4f}")
                    self.capture_intruder(frame)
        except Exception as e:
            self.logger.error(f"Error checking face landmarks: {e}")

    def capture_intruder(self, frame):
        try:
            import cv2
            from utils.paths import get_screenshot_dir
            base_folder = self.config_manager.Get("screenshot_folder", "screenshots")
            base_folder = get_screenshot_dir(base_folder)
                
            intruder_dir = os.path.join(base_folder, "intruders")
            os.makedirs(intruder_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(intruder_dir, f"intruder_{timestamp}.jpg")
            
            # Save frame as JPEG
            cv2.imwrite(filename, frame)
            self.logger.warning(f"Intruder screenshot saved: {filename}")
            
            if self.ui_callback:
                self.ui_callback("INTRUDER_ALERT", filename)
        except Exception as e:
            self.logger.error(f"Failed to capture intruder image: {e}")
