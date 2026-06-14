import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
from themes.theme_manager import ThemeManager

class SplashScreen(QWidget):
    def __init__(self, theme_name="Jarvis Theme"):
        super().__init__()
        self.theme_name = theme_name
        self.theme_meta = ThemeManager.GetThemeMeta(theme_name)
        
        # Set Frameless & Transparent Background
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.resize(500, 320)
        self.InitUI()
        
        # Opacity Fade-in Animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(1200)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()

        # Loading Progress Timer
        self.progress_val = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(25) # 40 steps per second

    def InitUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Futuristic Container Card
        card = QWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(10)
        
        # Get Accent Color from current Theme
        accent_color = self.theme_meta["accent"]
        bg_card = self.theme_meta["glass_card"]
        border_color = self.theme_meta["border"]
        
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_card};
                border: 2px solid {border_color};
                border-radius: 20px;
            }}
        """)
        
        # Title
        self.title_label = QLabel("GestureX")
        self.title_label.setFont(QFont("Outfit", 36, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"color: {accent_color}; border: none; background: transparent;")
        
        # Tagline
        self.tagline_label = QLabel("Control Beyond Touch")
        self.tagline_label.setFont(QFont("Outfit", 12, QFont.Weight.Medium))
        self.tagline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tagline_label.setStyleSheet(f"color: {self.theme_meta['subtext']}; border: none; background: transparent;")
        
        # Loading Progress Status Text
        self.status_label = QLabel("Initializing core modules...")
        self.status_label.setFont(QFont("Outfit", 9))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: rgba(255,255,255,0.7); border: none; background: transparent;")
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {accent_color};
                border-radius: 4px;
            }}
        """)
        
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.tagline_label)
        card_layout.addSpacing(25)
        card_layout.addWidget(self.status_label)
        card_layout.addWidget(self.progress_bar)
        
        layout.addWidget(card)
        self.setLayout(layout)

    def update_progress(self):
        self.progress_val += 1
        self.progress_bar.setValue(self.progress_val)
        
        # Dynamically change status messages
        if self.progress_val == 15:
            self.status_label.setText("Loading computer vision engine...")
        elif self.progress_val == 40:
            self.status_label.setText("Instantiating MediaPipe landmarker pipelines...")
        elif self.progress_val == 65:
            self.status_label.setText("Loading user profiles and QSS style structures...")
        elif self.progress_val == 85:
            self.status_label.setText("Connecting windows shell shortcuts...")
        elif self.progress_val >= 100:
            self.timer.stop()
            self.close_splash()

    def close_splash(self):
        # Fade-out animation
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.finished.connect(self.close)
        self.anim.start()
