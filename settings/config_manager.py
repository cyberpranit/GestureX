import os
import json
import logging

logger = logging.getLogger("GestureX.Config")

DEFAULT_CONFIG = {
    "camera_index": 0,
    "theme": "Jarvis Theme",
    "dark_mode": True,
    "startup_with_windows": False,
    "screenshot_folder": "screenshots",
    "air_mouse_speed": 1.5,
    "sensitivity": 1.0,
    "notifications_enabled": True,
    "modules": {
        "Volume Control": {"enabled": True, "sensitivity": 1.0},
        "Brightness Control": {"enabled": True, "sensitivity": 1.0},
        "Screenshot Gesture": {"enabled": True, "sensitivity": 1.0},
        "Air Mouse": {"enabled": False, "sensitivity": 1.0},
        "Media Controls": {"enabled": False, "sensitivity": 1.0},
        "Application Launcher": {"enabled": False, "sensitivity": 1.0},
        "Presentation Mode": {"enabled": False, "sensitivity": 1.0},
        "Gaming Mode": {"enabled": False, "sensitivity": 1.0},
        "Voice Assistant": {"enabled": False, "sensitivity": 1.0},
        "Air Writing": {"enabled": False, "sensitivity": 1.0},
        "Security Module": {"enabled": False, "sensitivity": 1.0},
        "System Information Overlay": {"enabled": False, "sensitivity": 1.0}
    },
    "gesture_mappings": {
        "Volume Control": {
            "hand": "Left",
            "gesture": "Thumb-Index Pinch"
        },
        "Brightness Control": {
            "hand": "Right",
            "gesture": "Thumb-Index Pinch"
        },
        "Screenshot Gesture": {
            "gesture": "Open Palm to Closed Fist"
        },
        "Air Mouse": {
            "move": "Index Finger",
            "left_click": "Thumb-Index Pinch",
            "right_click": "Thumb-Middle Pinch",
            "scroll": "Two Fingers"
        },
        "Media Controls": {
            "play_pause": "Thumb Up",
            "next_track": "Swipe Right",
            "prev_track": "Swipe Left"
        },
        "Application Launcher": {
            "VS Code": "V Gesture",
            "Chrome": "C Gesture",
            "Spotify": "S Gesture",
            "Steam": "W Gesture",
            "Genshin Impact": "G Gesture"
        },
        "Presentation Mode": {
            "next_slide": "Swipe Right",
            "prev_slide": "Swipe Left",
            "laser_pointer": "Open Palm"
        },
        "Gaming Mode": {
            "toggle_obs": "Three Fingers Up",
            "mute_mic": "Shaka Gesture"
        },
        "Security Module": {
            "lock_pc": "Both Palms Raised",
            "privacy_mode": "Five Fingers 3s"
        }
    }
}

class ConfigManager:
    def __init__(self, filepath=None):
        if filepath is None:
            # Put in the workspace path or next to application
            from utils.paths import get_user_data_dir
            self.filepath = os.path.join(get_user_data_dir(), "settings", "settings.json")
        else:
            self.filepath = filepath
            
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self.config = {}
        self.Load()

    def Load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.config = json.load(f)
                # Ensure all default keys exist
                self._merge_defaults(DEFAULT_CONFIG, self.config)
            except Exception as e:
                logger.error(f"Error loading configuration: {e}. Resetting to defaults.")
                self.config = json.loads(json.dumps(DEFAULT_CONFIG))
                self.Save()
        else:
            self.config = json.loads(json.dumps(DEFAULT_CONFIG))
            self.Save()

    def _merge_defaults(self, default, current):
        """Recursively merges default config into loaded config for backward/forward compatibility."""
        for k, v in default.items():
            if k not in current:
                current[k] = json.loads(json.dumps(v))
            elif isinstance(v, dict) and isinstance(current[k], dict):
                self._merge_defaults(v, current[k])

    def Save(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def Get(self, key, default=None):
        return self.config.get(key, default)

    def Set(self, key, value):
        self.config[key] = value
        self.Save()

    def GetModuleSetting(self, module_name, key, default=None):
        modules = self.config.get("modules", {})
        module = modules.get(module_name, {})
        return module.get(key, default)

    def SetModuleSetting(self, module_name, key, value):
        if "modules" not in self.config:
            self.config["modules"] = {}
        if module_name not in self.config["modules"]:
            self.config["modules"][module_name] = {}
        self.config["modules"][module_name][key] = value
        self.Save()

    def IsModuleEnabled(self, module_name):
        return self.GetModuleSetting(module_name, "enabled", False)

    def ResetToDefaults(self):
        self.config = json.loads(json.dumps(DEFAULT_CONFIG))
        self.Save()
