import time
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPoint, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush
from themes.theme_manager import ThemeManager

# ----------------------------------------------------
# 1. SLIDING VOLUME & BRIGHTNESS HUD OVERLAY
# ----------------------------------------------------
class HUDOverlay(QWidget):
    def __init__(self, mode="Volume", theme_name="Jarvis Theme"):
        super().__init__()
        self.mode = mode
        self.value = 50
        self.theme_meta = ThemeManager.GetThemeMeta(theme_name)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.resize(320, 90)
        self.InitUI()
        
        # Hide timer
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def InitUI(self):
        layout = QVBoxLayout()
        self.card = QWidget()
        self.card_layout = QHBoxLayout(self.card)
        self.card_layout.setContentsMargins(15, 10, 15, 10)
        
        accent = self.theme_meta["accent"]
        bg = self.theme_meta["glass_card"]
        border = self.theme_meta["border"]
        
        self.card.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 15px;
            }}
        """)
        
        self.icon_label = QLabel(self.mode[0].upper()) # V or B
        self.icon_label.setFont(QFont("Outfit", 18, QFont.Weight.Bold))
        self.icon_label.setStyleSheet(f"color: {accent}; border: none; background: transparent;")
        
        self.label = QLabel(f"{self.mode}: {self.value}%")
        self.label.setFont(QFont("Outfit", 12, QFont.Weight.Medium))
        self.label.setStyleSheet("color: white; border: none; background: transparent;")
        
        self.card_layout.addWidget(self.icon_label)
        self.card_layout.addWidget(self.label)
        self.card_layout.addStretch()
        
        layout.addWidget(self.card)
        self.setLayout(layout)

    def SetTheme(self, theme_name):
        self.theme_meta = ThemeManager.GetThemeMeta(theme_name)
        accent = self.theme_meta["accent"]
        bg = self.theme_meta["glass_card"]
        border = self.theme_meta["border"]
        self.card.setStyleSheet(f"background-color: {bg}; border: 2px solid {border}; border-radius: 15px;")
        self.icon_label.setStyleSheet(f"color: {accent}; border: none; background: transparent;")
        self.update()

    def UpdateValue(self, value):
        self.value = value
        self.label.setText(f"{self.mode}: {self.value}%")
        
        # Reposition to center top of screen
        screen_geo = QApplication_screen_geometry()
        x = (screen_geo.width() - self.width()) // 2
        y = 80 # 80 pixels from top
        self.move(x, y)
        
        self.show()
        # Reset hide timer (2 seconds)
        self.hide_timer.start(2000)

    def paintEvent(self, event):
        # Draw a custom progress bar in overlay background
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        accent = QColor(self.theme_meta["accent"])
        painter.setPen(Qt.PenStyle.NoPen)
        # Background bar
        painter.setBrush(QBrush(QColor(255, 255, 255, 20)))
        painter.drawRoundedRect(15, 68, self.width() - 30, 6, 3, 3)
        
        # Fill bar
        painter.setBrush(QBrush(accent))
        fill_w = int((self.width() - 30) * (self.value / 100.0))
        painter.drawRoundedRect(15, 68, fill_w, 6, 3, 3)

def QApplication_screen_geometry():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        screen = app.primaryScreen()
        if screen:
            return screen.geometry()
    return QRectF(0, 0, 1920, 1080)


# ----------------------------------------------------
# 2. LASER POINTER OVERLAY
# ----------------------------------------------------
class LaserPointerCanvas(QWidget):
    def __init__(self):
        super().__init__()
        # Translucent, click-through, and stays on top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) # Click through!
        
        # Fill primary screen size
        screen_geo = QApplication_screen_geometry()
        self.setGeometry(0, 0, int(screen_geo.width()), int(screen_geo.height()))
        
        self.laser_pos = None

    def UpdateLaserPos(self, x, y):
        if x is None or y is None:
            self.laser_pos = None
            self.hide()
        else:
            self.laser_pos = QPoint(x, y)
            self.show()
            self.update()

    def paintEvent(self, event):
        if not self.laser_pos:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw glowing laser pointer dot (red circle with gradient glow)
        glow_color = QColor(255, 0, 0, 50)
        center_color = QColor(255, 50, 50, 255)
        
        # Outer glow
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow_color))
        painter.drawEllipse(self.laser_pos, 18, 18)
        
        # Center core
        painter.setBrush(QBrush(center_color))
        painter.drawEllipse(self.laser_pos, 7, 7)


# ----------------------------------------------------
# 3. AIR WRITING CANVAS OVERLAY
# ----------------------------------------------------
class WritingCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) # Click through!
        
        screen_geo = QApplication_screen_geometry()
        self.setGeometry(0, 0, int(screen_geo.width()), int(screen_geo.height()))
        
        self.strokes = []
        self.status_text = ""

    def UpdateCanvas(self, strokes, text=""):
        if strokes is None:
            self.strokes = []
            self.status_text = ""
            self.hide()
        else:
            self.strokes = strokes
            self.status_text = text
            self.show()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw the strokes
        pen = QPen(QColor(0, 255, 200, 230), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundLine, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        w, h = self.width(), self.height()
        
        for stroke in self.strokes:
            if len(stroke) < 2:
                continue
            for i in range(len(stroke) - 1):
                pt1 = stroke[i]
                pt2 = stroke[i+1]
                # Scale float (0.0-1.0) coordinates to screen size
                p1 = QPoint(int(pt1[0] * w), int(pt1[1] * h))
                p2 = QPoint(int(pt2[0] * w), int(pt2[1] * h))
                painter.drawLine(p1, p2)

        # Draw status text at the bottom center of the screen
        if self.status_text:
            painter.setPen(QColor(255, 255, 255, 230))
            painter.setFont(QFont("Outfit", 16, QFont.Weight.DemiBold))
            rect = QRectF(0, h - 150, w, 60)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.status_text)


# ----------------------------------------------------
# 4. FLOATING SYSTEM INFORMATION OVERLAY WIDGET
# ----------------------------------------------------
class SystemInfoWidget(QWidget):
    def __init__(self, theme_name="Jarvis Theme"):
        super().__init__()
        self.theme_meta = ThemeManager.GetThemeMeta(theme_name)
        
        # Transparent background, stays on top, tool window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.resize(220, 180)
        self.drag_position = QPoint()
        
        self.metrics = None
        self.InitUI()
        
        # Default positioning: Top Right corner
        screen_geo = QApplication_screen_geometry()
        self.move(int(screen_geo.width() - self.width() - 40), 100)

    def InitUI(self):
        self.layout = QVBoxLayout()
        self.card = QWidget()
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(15, 15, 15, 15)
        self.card_layout.setSpacing(6)
        
        self.ApplyThemeStyle()
        
        # Drag header bar
        self.header = QLabel("SYS MONITOR")
        self.header.setFont(QFont("Outfit", 9, QFont.Weight.Bold))
        self.header.setStyleSheet(f"color: {self.theme_meta['accent']}; border: none; background: transparent;")
        
        # CPU
        self.cpu_label = QLabel("CPU Usage: 0%")
        self.cpu_label.setFont(QFont("Outfit", 10))
        self.cpu_label.setStyleSheet("color: white; border: none; background: transparent;")
        
        # RAM
        self.ram_label = QLabel("RAM Usage: 0%")
        self.ram_label.setFont(QFont("Outfit", 10))
        self.ram_label.setStyleSheet("color: white; border: none; background: transparent;")

        # Battery
        self.battery_label = QLabel("Battery: 100%")
        self.battery_label.setFont(QFont("Outfit", 10))
        self.battery_label.setStyleSheet("color: white; border: none; background: transparent;")

        # FPS / Profile
        self.fps_label = QLabel("FPS: 0.0 | Jarvis")
        self.fps_label.setFont(QFont("Outfit", 10))
        self.fps_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); border: none; background: transparent;")

        self.card_layout.addWidget(self.header)
        self.card_layout.addWidget(self.cpu_label)
        self.card_layout.addWidget(self.ram_label)
        self.card_layout.addWidget(self.battery_label)
        self.card_layout.addWidget(self.fps_label)
        
        self.layout.addWidget(self.card)
        self.setLayout(self.layout)

    def SetTheme(self, theme_name):
        self.theme_meta = ThemeManager.GetThemeMeta(theme_name)
        self.ApplyThemeStyle()
        self.header.setStyleSheet(f"color: {self.theme_meta['accent']}; border: none; background: transparent;")

    def ApplyThemeStyle(self):
        bg = self.theme_meta["glass_card"]
        border = self.theme_meta["border"]
        self.card.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 12px;
            }}
        """)

    def UpdateMetrics(self, metrics):
        if metrics is None:
            self.metrics = None
            self.hide()
            return
            
        self.metrics = metrics
        self.cpu_label.setText(f"CPU Usage: {metrics['cpu']}%")
        self.ram_label.setText(f"RAM Usage: {metrics['ram']}%")
        
        bat_status = "Charged" if metrics["plugged"] else "Discharging"
        self.battery_label.setText(f"Battery: {metrics['battery']}% ({bat_status})")
        self.fps_label.setText(f"FPS: {metrics['fps']} | {metrics['profile']}")
        
        self.show()

    # ----------------------------------------------------
    # DRAG AND DROP HANDLERS (Allow moving widget)
    # ----------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
