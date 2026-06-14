import logging

class GestureModule:
    def __init__(self, name, description, config_manager):
        self.name = name
        self.description = description
        self.config_manager = config_manager
        self.enabled = False
        self.logger = logging.getLogger(f"GestureX.Module.{self.name.replace(' ', '')}")

    def Enable(self):
        if not self.enabled:
            self.enabled = True
            self.logger.info(f"Module {self.name} enabled.")
            self.on_enable()

    def Disable(self):
        if self.enabled:
            self.enabled = False
            self.logger.info(f"Module {self.name} disabled.")
            self.on_disable()

    def on_enable(self):
        """Override to implement logic when the module is enabled."""
        pass

    def on_disable(self):
        """Override to implement logic when the module is disabled."""
        pass

    def LoadSettings(self):
        """Load settings custom to this module."""
        pass

    def SaveSettings(self):
        """Save settings custom to this module."""
        pass

    def process_hand_landmarks(self, hands_data, frame_size):
        """
        Process detected hand landmarks.
        hands_data: A list of dicts, each containing:
            'landmarks': list of (x, y, z) normalized float coordinates
            'handedness': "Left" or "Right"
        frame_size: tuple (width, height)
        """
        pass
