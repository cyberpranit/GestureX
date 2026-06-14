import sys
import logging
from PyQt6.QtWidgets import QApplication
from ui.dashboard import DashboardWindow
from ui.splash import SplashScreen
from settings.config_manager import ConfigManager
from utils.logger import SetupLogger

def main():
    # 1. Setup application-wide logging
    logger = SetupLogger()
    logger.info("Initializing GestureX...")

    # 2. Start QApp
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Essential so minimizing to tray doesn't quit the app

    # 3. Read current theme from settings to style the splash screen
    config = ConfigManager()
    theme = config.Get("theme", "Jarvis Theme")

    # 4. Show animated splash screen
    splash = SplashScreen(theme)
    splash.show()

    # 5. Dashboard loading
    dashboard = DashboardWindow()

    # When splash closes (finished progress), show dashboard
    # The splash timer stops at 100 and calls self.close() which triggers the fade out.
    # We delay showing the dashboard slightly to align with the fade-out duration.
    def show_dashboard():
        dashboard.show()
        logger.info("Dashboard loaded and visible.")

    # We hook a timer or callback
    # Let's check when the splash screen is closed or set a timer matching splash duration
    # Splash runs 100 ticks of 25ms = 2.5s.
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(2600, show_dashboard)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
