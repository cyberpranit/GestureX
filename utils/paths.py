import os
import sys

def get_project_dir():
    """Returns the root directory of the project when running from source or the bundle dir when frozen."""
    if getattr(sys, 'frozen', False):
        # In PyInstaller bundle, sys._MEIPASS is the temp folder
        return getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_user_data_dir():
    """Returns the directory where application configuration, profiles, and logs should be stored."""
    if getattr(sys, 'frozen', False):
        # Production mode: store in standard Windows APPDATA folder
        appdata = os.environ.get('APPDATA')
        if not appdata:
            appdata = os.path.expanduser('~')
        return os.path.join(appdata, 'GestureX')
    else:
        # Development mode: store locally in the project directory
        return get_project_dir()

def get_screenshot_dir(configured_folder="screenshots"):
    """Returns the absolute path to the folder where screenshots and intruder images should be saved."""
    if os.path.isabs(configured_folder):
        return configured_folder
    
    if getattr(sys, 'frozen', False):
        # Production mode: default 'screenshots' folder maps to user's Pictures/GestureX folder
        if configured_folder == "screenshots":
            pictures_dir = os.path.join(os.path.expanduser('~'), 'Pictures')
            if os.path.exists(pictures_dir):
                return os.path.join(pictures_dir, 'GestureX')
            else:
                return os.path.join(os.path.expanduser('~'), 'GestureX', 'screenshots')
        else:
            # If they custom configured another relative folder name, save it inside user data directory
            return os.path.join(get_user_data_dir(), configured_folder)
    else:
        # Development mode: save inside project directory
        return os.path.join(get_project_dir(), configured_folder)
