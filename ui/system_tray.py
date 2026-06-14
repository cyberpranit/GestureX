from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

class SystemTrayManager(QSystemTrayIcon):
    def __init__(self, main_window, profile_manager, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.profile_manager = profile_manager
        
        # Initialize Dynamic Icon to prevent file path issues
        self.setIcon(self.CreateDynamicIcon())
        self.setToolTip("GestureX - Control Beyond Touch")
        
        self.InitMenu()
        
        # Double click activates show/hide dashboard
        self.activated.connect(self.OnTrayActivated)

    def CreateDynamicIcon(self):
        # Programmatically draw a clean neon icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw outer cyan ring
        painter.setPen(QColor(0, 210, 255, 200))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(2, 2, 28, 28)
        
        # Draw inner cyan dot
        painter.setBrush(QColor(0, 210, 255, 255))
        painter.drawEllipse(11, 11, 10, 10)
        
        painter.end()
        return QIcon(pixmap)

    def InitMenu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #0b1528;
                color: #00d2ff;
                border: 1px solid #00d2ff;
            }
            QMenu::item:selected {
                background-color: #00d2ff;
                color: black;
            }
        """)

        # Show/Hide action
        self.toggle_action = menu.addAction("Show Dashboard")
        self.toggle_action.triggered.connect(self.ToggleDashboard)

        # Profiles submenu
        profile_menu = menu.addMenu("Quick Profiles")
        self.RefreshProfilesSubmenu(profile_menu)

        menu.addSeparator()

        # Exit action
        exit_action = menu.addAction("Exit GestureX")
        exit_action.triggered.connect(self.main_window.QuitApplication)

        self.setContextMenu(menu)

    def RefreshProfilesSubmenu(self, menu):
        profiles = self.profile_manager.ListProfiles()
        for prof in profiles:
            action = menu.addAction(prof)
            # Use default capture lambda to preserve variable value
            action.triggered.connect(lambda checked=False, p=prof: self.ChangeProfile(p))

    def ChangeProfile(self, profile_name):
        self.main_window.LoadProfileByName(profile_name)

    def ToggleDashboard(self):
        if self.main_window.isVisible():
            self.main_window.hide()
            self.toggle_action.setText("Show Dashboard")
        else:
            self.main_window.showNormal()
            self.main_window.activateWindow()
            self.toggle_action.setText("Hide Dashboard")

    def OnTrayActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.ToggleDashboard()
