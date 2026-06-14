import os
import sys
import ctypes
import logging
import subprocess
import winreg

logger = logging.getLogger("GestureX.SysUtils")

# Global flags for pycaw and brightness controls
PYCAW_AVAILABLE = False
SBC_AVAILABLE = False

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except Exception as e:
    logger.warning(f"Pycaw is not fully available or comtypes initialization failed: {e}")

try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except Exception as e:
    logger.warning(f"screen_brightness_control library not available: {e}")

# ----------------------------------------------------
# VOLUME UTILITIES
# ----------------------------------------------------
import threading
import time

class HardwareWorker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.pending = {}
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.running = True

    def queue_action(self, action_type, value):
        with self.lock:
            # Enqueue the latest value, overwriting any previous unhandled requests of the same type (deduplication)
            self.pending[action_type] = value
            self.condition.notify()

    def run(self):
        while self.running:
            action = None
            with self.lock:
                while not self.pending and self.running:
                    self.condition.wait(timeout=0.05)
                if not self.running:
                    break
                if self.pending:
                    action_type = next(iter(self.pending))
                    value = self.pending.pop(action_type)
                    action = (action_type, value)
            
            if action:
                action_type, value = action
                try:
                    if action_type == "volume":
                        _SetSystemVolumeSync(value)
                    elif action_type == "brightness":
                        _SetSystemBrightnessSync(value)
                except Exception as e:
                    logger.error(f"Error in background hardware task: {e}")

_WORKER = HardwareWorker()
_WORKER.start()

def _SetSystemVolumeSync(percent):
    """Sets the master system volume percentage (0-100)."""
    percent = max(0, min(100, percent))
    if not PYCAW_AVAILABLE:
        return False
    try:
        ctypes.windll.ole32.CoInitialize()
        
        speakers = AudioUtilities.GetSpeakers()
        if speakers:
            volume = speakers.EndpointVolume
            # Set volume scalar (0.0 to 1.0)
            volume.SetMasterVolumeLevelScalar(percent / 100.0, None)
            return True
    except Exception as e:
        logger.error(f"Error setting volume: {e}")
        return False
    finally:
        try:
            ctypes.windll.ole32.CoUninitialize()
        except:
            pass
    return False

def SetSystemVolume(percent):
    if not PYCAW_AVAILABLE:
        return False
    _WORKER.queue_action("volume", percent)
    return True

def GetSystemVolume():
    """Returns the current master system volume percentage (0-100)."""
    if not PYCAW_AVAILABLE:
        return 50
    try:
        ctypes.windll.ole32.CoInitialize()
        speakers = AudioUtilities.GetSpeakers()
        if speakers:
            volume = speakers.EndpointVolume
            vol_scalar = volume.GetMasterVolumeLevelScalar()
            return int(round(vol_scalar * 100.0))
    except Exception as e:
        logger.error(f"Error getting volume: {e}")
        return 50
    finally:
        try:
            ctypes.windll.ole32.CoUninitialize()
        except:
            pass

# ----------------------------------------------------
# BRIGHTNESS UTILITIES
# ----------------------------------------------------
def _SetSystemBrightnessSync(percent):
    """Sets the monitor brightness percentage (0-100)."""
    percent = max(0, min(100, percent))
    if not SBC_AVAILABLE:
        return False
    try:
        sbc.set_brightness(percent)
        return True
    except Exception as e:
        logger.error(f"Error setting brightness: {e}")
        # Try fall back to WMI if SBC fails
        try:
            import wmi
            c = wmi.WMI(namespace="wmi")
            methods = c.WmiMonitorBrightnessMethods()
            if methods:
                methods[0].WmiSetBrightness(percent, 0)
                return True
        except Exception as wmi_err:
            logger.error(f"Fallback WMI brightness set failed: {wmi_err}")
        return False

def SetSystemBrightness(percent):
    if not SBC_AVAILABLE:
        return False
    _WORKER.queue_action("brightness", percent)
    return True

def GetSystemBrightness():
    """Gets the current monitor brightness percentage (0-100)."""
    if not SBC_AVAILABLE:
        return 50
    try:
        val = sbc.get_brightness()
        if isinstance(val, list):
            return val[0]
        return val
    except Exception as e:
        logger.error(f"Error getting brightness: {e}")
        return 50

# ----------------------------------------------------
# HARDWARE MUTE UTILITIES
# ----------------------------------------------------
def SetMicrophoneMute(mute=True):
    """Mutes or unmutes the default system capture device (microphone)."""
    if not PYCAW_AVAILABLE:
        logger.warning("Microphone mute control unavailable.")
        return False
    try:
        ctypes.windll.ole32.CoInitialize()
        mic = AudioUtilities.GetMicrophone()
        if mic:
            interface = mic.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(mute, None)
            logger.info(f"Microphone mute state set to: {mute}")
            return True
    except Exception as e:
        logger.error(f"Error setting microphone mute: {e}")
        return False
    finally:
        try:
            ctypes.windll.ole32.CoUninitialize()
        except:
            pass

# ----------------------------------------------------
# OTHER WIN32 SYSTEM ACTIONS
# ----------------------------------------------------
def LockPC():
    """Locks the Windows workstation immediately."""
    try:
        ctypes.windll.user32.LockWorkStation()
        logger.info("Workstation locked successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to lock workstation: {e}")
        return False

def ToggleStartup(enabled=True):
    """Adds or removes the application from Windows Startup registry."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "GestureX"
    app_path = f'"{os.path.abspath(sys.argv[0])}" --minimized'
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            logger.info("Added GestureX to Windows Startup Registry.")
        else:
            try:
                winreg.DeleteValue(key, app_name)
                logger.info("Removed GestureX from Windows Startup Registry.")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        logger.error(f"Error updating Windows startup key: {e}")
        return False
