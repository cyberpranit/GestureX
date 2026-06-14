import unittest
import os
import sys

# Add project root to path to ensure clean imports during standalone runs
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from settings.config_manager import ConfigManager, DEFAULT_CONFIG
from profiles.profile_manager import ProfileManager
from themes.theme_manager import ThemeManager
from core.module_manager import ModuleManager

class TestGestureXCore(unittest.TestCase):
    def setUp(self):
        # Setup temporary settings config
        self.test_settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings", "settings_test.json")
        self.config = ConfigManager(self.test_settings_path)
        self.profile_mgr = ProfileManager(self.config)

    def tearDown(self):
        # Cleanup test config file
        if os.path.exists(self.test_settings_path):
            try:
                os.remove(self.test_settings_path)
            except:
                pass

    def test_default_modules_state(self):
        """Verify design philosophy: only 3 core modules enabled by default."""
        self.config.ResetToDefaults()
        
        # Test enabled by default
        self.assertTrue(self.config.IsModuleEnabled("Volume Control"))
        self.assertTrue(self.config.IsModuleEnabled("Brightness Control"))
        self.assertTrue(self.config.IsModuleEnabled("Screenshot Gesture"))
        
        # Test others disabled by default
        self.assertFalse(self.config.IsModuleEnabled("Air Mouse"))
        self.assertFalse(self.config.IsModuleEnabled("Media Controls"))
        self.assertFalse(self.config.IsModuleEnabled("Application Launcher"))
        self.assertFalse(self.config.IsModuleEnabled("Voice Assistant"))

    def test_profile_switching(self):
        """Verify switching profiles updates configurations correctly."""
        self.config.ResetToDefaults()
        
        # Switch to Gaming profile
        success = self.profile_mgr.LoadProfile("Gaming")
        self.assertTrue(success)
        
        # Verify Gaming mode modules config
        self.assertTrue(self.config.IsModuleEnabled("Gaming Mode"))
        self.assertTrue(self.config.IsModuleEnabled("System Information Overlay"))
        self.assertFalse(self.config.IsModuleEnabled("Brightness Control"))
        self.assertEqual(self.config.Get("theme"), "Cyberpunk Theme")

    def test_theme_manager(self):
        """Verify theme manager has all 4 requested themes and outputs stylesheets."""
        themes = ["Matrix Theme", "Cyberpunk Theme", "Jarvis Theme", "Minimal Theme"]
        for t in themes:
            self.assertIn(t, ThemeManager.THEMES)
            qss = ThemeManager.GetStylesheet(t)
            self.assertTrue(len(qss) > 100)

    def test_module_manager_loading(self):
        """Verify module manager registers all 12 modules."""
        manager = ModuleManager(self.config)
        manager.InitializeModules()
        modules = manager.GetModules()
        
        self.assertEqual(len(modules), 12)
        self.assertIn("Volume Control", modules)
        self.assertIn("Brightness Control", modules)
        self.assertIn("Screenshot Gesture", modules)
        self.assertIn("Air Mouse", modules)
        self.assertIn("Security Module", modules)

    def test_volume_calculation(self):
        """Verify volume control processes landmarks and calculates values."""
        manager = ModuleManager(self.config)
        manager.InitializeModules()
        vol_module = manager.GetModules()["Volume Control"]
        
        # Set a mock callback
        output_vals = []
        vol_module.ui_callback = lambda val: output_vals.append(val)
        vol_module.Enable()

        # Mock left hand landmark data (pinched state)
        # Thumb tip (4) and Index tip (8) are identical coordinates
        mock_hands_pinch = [{
            "handedness": "Left",
            "landmarks": {
                4: (0.5, 0.5, 0.0),
                8: (0.5, 0.5, 0.0)
            }
        }]
        
        for _ in range(5):
            vol_module.process_hand_landmarks(mock_hands_pinch, (640, 480))
        # Value should map to minimum volume (0%)
        self.assertIn(0, output_vals)

        # Mock left hand landmark data (stretched state)
        # Thumb tip (4) and Index tip (8) are far apart
        mock_hands_wide = [{
            "handedness": "Left",
            "landmarks": {
                4: (0.1, 0.1, 0.0),
                8: (0.9, 0.9, 0.0)
            }
        }]
        for _ in range(5):
            vol_module.process_hand_landmarks(mock_hands_wide, (640, 480))
        # Value should map to max volume (100%)
        self.assertIn(100, output_vals)

if __name__ == "__main__":
    unittest.main()
