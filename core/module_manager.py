import logging

# Module Imports
from modules.volume_module import VolumeModule
from modules.brightness_module import BrightnessModule
from modules.screenshot_module import ScreenshotModule
from modules.mouse_module import MouseModule
from modules.media_module import MediaModule
from modules.launcher_module import LauncherModule
from modules.presentation_module import PresentationModule
from modules.gaming_module import GamingModule
from modules.voice_module import VoiceModule
from modules.writing_module import WritingModule
from modules.security_module import SecurityModule
from modules.sysinfo_module import SysInfoModule

logger = logging.getLogger("GestureX.ModuleManager")

class ModuleManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.modules = {}
        
        # Callbacks registration (to be hooked by the main UI/Dashboard)
        self.callbacks = {
            "volume": None,
            "brightness": None,
            "screenshot": None,
            "presentation": None, # for laser pointer
            "gaming": None,
            "voice": None,
            "writing": None,
            "security": None,
            "sysinfo": None
        }

    def InitializeModules(self):
        """Instantiate all available modules with respective callbacks."""
        self.modules = {
            "Volume Control": VolumeModule(
                "Volume Control", 
                "Control system volume using LEFT hand pinch distance.", 
                self.config,
                ui_callback=lambda val: self.trigger_callback("volume", val)
            ),
            "Brightness Control": BrightnessModule(
                "Brightness Control", 
                "Control screen brightness using RIGHT hand pinch distance.", 
                self.config,
                ui_callback=lambda val: self.trigger_callback("brightness", val)
            ),
            "Screenshot Gesture": ScreenshotModule(
                "Screenshot Gesture", 
                "Capture screenshot by closing open palm into fist.", 
                self.config,
                ui_callback=lambda path: self.trigger_callback("screenshot", path)
            ),
            "Air Mouse": MouseModule(
                "Air Mouse", 
                "Control cursor, click and scroll with RIGHT hand index finger.", 
                self.config
            ),
            "Media Controls": MediaModule(
                "Media Controls", 
                "Play/Pause with Thumb Up, Skip tracks with Left/Right swipes.", 
                self.config
            ),
            "Application Launcher": LauncherModule(
                "Application Launcher", 
                "Launch VS Code, Chrome, Spotify, Steam using specific hand signs.", 
                self.config
            ),
            "Presentation Mode": PresentationModule(
                "Presentation Mode", 
                "Control slides with swipes and enable laser pointer with open palm.", 
                self.config,
                ui_callback=lambda x, y: self.trigger_callback("presentation", (x, y))
            ),
            "Gaming Mode": GamingModule(
                "Gaming Mode", 
                "Mute system mic and toggle OBS recording using shaka and 3-fingers.", 
                self.config,
                ui_callback=lambda msg: self.trigger_callback("gaming", msg)
            ),
            "Voice Assistant": VoiceModule(
                "Voice Assistant", 
                "Hold open palm for 2 seconds to activate voice command recognition.", 
                self.config,
                ui_callback=lambda msg: self.trigger_callback("voice", msg)
            ),
            "Air Writing": WritingModule(
                "Air Writing", 
                "Draw in air with index finger and convert handwriting to clipboard text.", 
                self.config,
                ui_callback=lambda strokes, txt: self.trigger_callback("writing", (strokes, txt))
            ),
            "Security Module": SecurityModule(
                "Security Module", 
                "Lock PC with double palm, mute/blur with 5 fingers, capture intruders.", 
                self.config,
                ui_callback=lambda action, val: self.trigger_callback("security", (action, val))
            ),
            "System Information Overlay": SysInfoModule(
                "System Information Overlay", 
                "Show real-time floating widgets of CPU, Memory, battery and FPS.", 
                self.config,
                ui_callback=lambda stats: self.trigger_callback("sysinfo", stats)
            )
        }

        # Apply initial enabling/disabling based on config
        self.RefreshModuleStates()

    def RegisterCallback(self, event_name, func):
        if event_name in self.callbacks:
            self.callbacks[event_name] = func
            logger.debug(f"Registered UI callback for event: {event_name}")

    def trigger_callback(self, event_name, value):
        func = self.callbacks.get(event_name)
        if func:
            func(value)

    def RefreshModuleStates(self):
        """Enables or disables modules matching the configurations state."""
        for name, module in self.modules.items():
            should_enable = self.config.IsModuleEnabled(name)
            if should_enable and not module.enabled:
                try:
                    module.Enable()
                except Exception as e:
                    logger.error(f"Error enabling module {name}: {e}")
            elif not should_enable and module.enabled:
                try:
                    module.Disable()
                except Exception as e:
                    logger.error(f"Error disabling module {name}: {e}")

    def GetModules(self):
        return self.modules

    def ProcessHandLandmarks(self, hands_data, frame_size):
        """Routes landmark updates to all enabled modules."""
        for module in self.modules.values():
            if module.enabled:
                try:
                    module.process_hand_landmarks(hands_data, frame_size)
                except Exception as e:
                    logger.error(f"Error processing hands in module {module.name}: {e}")

    def ProcessFaceLandmarks(self, face_landmarks, frame, frame_size):
        """Routes face landmarks specifically to the Security Module if enabled."""
        sec_module = self.modules.get("Security Module")
        if sec_module and sec_module.enabled:
            try:
                sec_module.process_face_landmarks(face_landmarks, frame, frame_size)
            except Exception as e:
                logger.error(f"Error processing face in Security Module: {e}")
