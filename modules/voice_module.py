import os
import time
import threading
import subprocess
import webbrowser
from modules.base_module import GestureModule

# Optional SpeechRecognition import
SR_AVAILABLE = False
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except Exception:
    pass

class VoiceModule(GestureModule):
    def __init__(self, name, description, config_manager, ui_callback=None):
        super().__init__(name, description, config_manager)
        self.ui_callback = ui_callback # For notifications (e.g. "Listening...", "Command: Browser")
        
        # Open palm held timer
        self.palm_hold_start = 0.0
        self.palm_active = False
        self.hold_threshold = 2.0 # 2 seconds hold
        
        self.is_listening = False
        self.cooldown_until = 0.0
        self.cooldown_duration = 5.0

    def on_enable(self):
        self.palm_hold_start = 0.0
        self.palm_active = False
        self.is_listening = False
        self.cooldown_until = 0.0

    def process_hand_landmarks(self, hands_data, frame_size):
        if self.is_listening:
            return

        current_time = time.time()
        if current_time < self.cooldown_until:
            return

        if not hands_data:
            self.palm_active = False
            return

        hand = hands_data[0]
        landmarks = hand['landmarks']

        is_palm = self.check_open_palm(landmarks)
        if is_palm:
            if not self.palm_active:
                self.palm_active = True
                self.palm_hold_start = current_time
                self.logger.debug("Voice Assistant: Open Palm detected. Hold for 2s...")
            else:
                if current_time - self.palm_hold_start >= self.hold_threshold:
                    self.logger.info("Voice Assistant: Triggering listening thread...")
                    self.is_listening = True
                    self.palm_active = False
                    # Start listening in a background thread to prevent UI freezing
                    threading.Thread(target=self.listen_and_execute, daemon=True).start()
        else:
            self.palm_active = False

    def check_open_palm(self, landmarks):
        # All fingers extended
        fingers_open = [
            landmarks[8][1] < landmarks[6][1],
            landmarks[12][1] < landmarks[10][1],
            landmarks[16][1] < landmarks[14][1],
            landmarks[20][1] < landmarks[18][1],
        ]
        return all(fingers_open)

    def listen_and_execute(self):
        if self.ui_callback:
            self.ui_callback("Listening...")

        if not SR_AVAILABLE:
            self.logger.warning("SpeechRecognition library or PyAudio is missing. Simulated speech listener.")
            time.sleep(2.0)
            if self.ui_callback:
                self.ui_callback("Speech recognition dependencies missing.")
            self.cleanup_listening()
            return

        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                # Adjust for ambient noise
                r.adjust_for_ambient_noise(source, duration=0.8)
                audio = r.listen(source, timeout=3, phrase_time_limit=3)

            self.logger.info("Voice Assistant: Audio captured. Analyzing speech...")
            if self.ui_callback:
                self.ui_callback("Processing...")

            command = r.recognize_google(audio).lower()
            self.logger.info(f"Voice Assistant: Recognized command: '{command}'")
            
            if self.ui_callback:
                self.ui_callback(f"Command: {command}")

            self.execute_command(command)
        except sr.WaitTimeoutError:
            self.logger.warning("Voice Assistant: Listening timed out.")
            if self.ui_callback:
                self.ui_callback("Listening timed out.")
        except sr.UnknownValueError:
            self.logger.warning("Voice Assistant: Speech not understood.")
            if self.ui_callback:
                self.ui_callback("Speech not understood.")
        except Exception as e:
            self.logger.error(f"Voice Assistant error: {e}")
            if self.ui_callback:
                self.ui_callback(f"Microphone error: {str(e)[:30]}")
        
        self.cleanup_listening()

    def cleanup_listening(self):
        self.is_listening = False
        self.cooldown_until = time.time() + self.cooldown_duration

    def execute_command(self, command):
        if "open browser" in command or "browser" in command or "chrome" in command:
            webbrowser.open("https://google.com")
        elif "open calculator" in command or "calculator" in command or "calc" in command:
            subprocess.Popen("calc.exe", shell=True)
        elif "search files" in command or "explorer" in command or "search" in command:
            # Open file explorer search
            subprocess.Popen("explorer.exe", shell=True)
        elif "shutdown" in command or "shutdown pc" in command:
            # Shutdown with a 2-minute safety warning, so user can cancel via 'shutdown /a'
            self.logger.warning("Voice Assistant triggered system shutdown (2 minute countdown).")
            os.system("shutdown /s /t 120")
            if self.ui_callback:
                self.ui_callback("Shutdown PC in 120s! Run 'shutdown /a' in command line to cancel.")
        else:
            self.logger.info(f"Voice Assistant: Command '{command}' did not match any triggers.")
