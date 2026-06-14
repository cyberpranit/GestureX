import os
import json
import logging

logger = logging.getLogger("GestureX.Profile")

class ProfileManager:
    def __init__(self, config_manager, profiles_dir=None):
        self.config_manager = config_manager
        if profiles_dir is None:
            self.profiles_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "profiles")
        else:
            self.profiles_dir = profiles_dir
            
        os.makedirs(self.profiles_dir, exist_ok=True)
        self.EnsureDefaultProfiles()

    def EnsureDefaultProfiles(self):
        # We will create default JSON profiles if they do not exist
        profiles = {
            "Normal": {
                "theme": "Jarvis Theme",
                "modules": {
                    "Volume Control": {"enabled": True},
                    "Brightness Control": {"enabled": True},
                    "Screenshot Gesture": {"enabled": True},
                    "Air Mouse": {"enabled": False},
                    "Media Controls": {"enabled": False},
                    "Application Launcher": {"enabled": False},
                    "Presentation Mode": {"enabled": False},
                    "Gaming Mode": {"enabled": False},
                    "Voice Assistant": {"enabled": False},
                    "Air Writing": {"enabled": False},
                    "Security Module": {"enabled": False},
                    "System Information Overlay": {"enabled": False}
                }
            },
            "Gaming": {
                "theme": "Cyberpunk Theme",
                "modules": {
                    "Volume Control": {"enabled": True},
                    "Brightness Control": {"enabled": False},
                    "Screenshot Gesture": {"enabled": True},
                    "Air Mouse": {"enabled": False},
                    "Media Controls": {"enabled": False},
                    "Application Launcher": {"enabled": False},
                    "Presentation Mode": {"enabled": False},
                    "Gaming Mode": {"enabled": True},
                    "Voice Assistant": {"enabled": False},
                    "Air Writing": {"enabled": False},
                    "Security Module": {"enabled": False},
                    "System Information Overlay": {"enabled": True}
                }
            },
            "Presentation": {
                "theme": "Minimal Theme",
                "modules": {
                    "Volume Control": {"enabled": True},
                    "Brightness Control": {"enabled": False},
                    "Screenshot Gesture": {"enabled": True},
                    "Air Mouse": {"enabled": False},
                    "Media Controls": {"enabled": False},
                    "Application Launcher": {"enabled": False},
                    "Presentation Mode": {"enabled": True},
                    "Gaming Mode": {"enabled": False},
                    "Voice Assistant": {"enabled": True},
                    "Air Writing": {"enabled": False},
                    "Security Module": {"enabled": False},
                    "System Information Overlay": {"enabled": False}
                }
            },
            "Productivity": {
                "theme": "Matrix Theme",
                "modules": {
                    "Volume Control": {"enabled": True},
                    "Brightness Control": {"enabled": True},
                    "Screenshot Gesture": {"enabled": True},
                    "Air Mouse": {"enabled": True},
                    "Media Controls": {"enabled": True},
                    "Application Launcher": {"enabled": True},
                    "Presentation Mode": {"enabled": False},
                    "Gaming Mode": {"enabled": False},
                    "Voice Assistant": {"enabled": False},
                    "Air Writing": {"enabled": True},
                    "Security Module": {"enabled": True},
                    "System Information Overlay": {"enabled": True}
                }
            }
        }

        for name, data in profiles.items():
            path = os.path.join(self.profiles_dir, f"{name}.json")
            if not os.path.exists(path):
                try:
                    with open(path, 'w') as f:
                        json.dump(data, f, indent=4)
                    logger.info(f"Created default profile: {name}")
                except Exception as e:
                    logger.error(f"Error creating profile {name}: {e}")

    def ListProfiles(self):
        profiles = []
        if os.path.exists(self.profiles_dir):
            for file in os.listdir(self.profiles_dir):
                if file.endswith(".json"):
                    profiles.append(file[:-5])
        return sorted(profiles)

    def LoadProfile(self, name):
        path = os.path.join(self.profiles_dir, f"{name}.json")
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    profile_data = json.load(f)
                
                # Apply theme if defined
                if "theme" in profile_data:
                    self.config_manager.Set("theme", profile_data["theme"])
                
                # Apply modules config
                if "modules" in profile_data:
                    for mod_name, mod_data in profile_data["modules"].items():
                        for k, v in mod_data.items():
                            self.config_manager.SetModuleSetting(mod_name, k, v)
                            
                logger.info(f"Loaded profile: {name}")
                return True
            except Exception as e:
                logger.error(f"Error loading profile {name}: {e}")
        return False

    def SaveCurrentAsProfile(self, name):
        """Save the current active configuration as a new profile."""
        profile_data = {
            "theme": self.config_manager.Get("theme"),
            "modules": self.config_manager.Get("modules")
        }
        path = os.path.join(self.profiles_dir, f"{name}.json")
        try:
            with open(path, 'w') as f:
                json.dump(profile_data, f, indent=4)
            logger.info(f"Saved custom profile: {name}")
            return True
        except Exception as e:
            logger.error(f"Error saving custom profile {name}: {e}")
            return False

    def ImportProfile(self, filepath):
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            # Basic validation
            if "modules" not in data:
                return False
            
            # Export to the profiles dir
            name = os.path.splitext(os.path.basename(filepath))[0]
            dest = os.path.join(self.profiles_dir, f"{name}.json")
            with open(dest, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error importing profile from {filepath}: {e}")
            return False

    def ExportProfile(self, name, filepath):
        src = os.path.join(self.profiles_dir, f"{name}.json")
        if not os.path.exists(src):
            return False
        try:
            with open(src, 'r') as f:
                data = json.load(f)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error exporting profile {name} to {filepath}: {e}")
            return False
