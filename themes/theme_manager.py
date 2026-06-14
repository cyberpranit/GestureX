class ThemeManager:
    THEMES = {
        "Matrix Theme": {
            "accent": "#00FF41",
            "bg_gradient": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #000000, stop:1 #0b1d12)",
            "glass_card": "rgba(10, 25, 15, 0.75)",
            "border": "rgba(0, 255, 65, 0.3)",
            "text": "#00FF41",
            "subtext": "#008F11",
            "qss": """
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #000000, stop:1 #0b1d12);
                    color: #00FF41;
                    font-family: 'Courier New', monospace;
                }
                QTabWidget::pane {
                    border: 1px solid rgba(0, 255, 65, 0.3);
                    border-radius: 12px;
                    background: rgba(10, 25, 15, 0.75);
                }
                QTabBar::tab {
                    background: rgba(0, 0, 0, 0.8);
                    color: #008F11;
                    border: 1px solid rgba(0, 255, 65, 0.2);
                    border-bottom: none;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: rgba(10, 25, 15, 0.85);
                    color: #00FF41;
                    border: 1px solid rgba(0, 255, 65, 0.5);
                    border-bottom: none;
                }
                QTabBar::tab:hover {
                    color: #00FF41;
                    background: rgba(0, 50, 15, 0.5);
                }
                QGroupBox {
                    border: 1px solid rgba(0, 255, 65, 0.3);
                    border-radius: 8px;
                    margin-top: 1.5em;
                    font-weight: bold;
                    color: #00FF41;
                    padding: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
                QPushButton {
                    background-color: rgba(0, 20, 5, 0.8);
                    color: #00FF41;
                    border: 1px solid #00FF41;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00FF41;
                    color: #000000;
                }
                QPushButton:pressed {
                    background-color: #008F11;
                }
                QCheckBox {
                    color: #00FF41;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 1px solid #00FF41;
                    border-radius: 3px;
                    background-color: black;
                }
                QCheckBox::indicator:checked {
                    background-color: #00FF41;
                }
                QLabel {
                    color: #00FF41;
                }
                QSlider::groove:horizontal {
                    border: 1px solid rgba(0, 255, 65, 0.3);
                    height: 8px;
                    background: black;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #00FF41;
                    border: 1px solid #00FF41;
                    width: 16px;
                    margin: -4px 0;
                    border-radius: 8px;
                }
                QComboBox {
                    background-color: black;
                    border: 1px solid rgba(0, 255, 65, 0.3);
                    border-radius: 4px;
                    padding: 5px;
                    color: #00FF41;
                }
                QComboBox QAbstractItemView {
                    background-color: black;
                    border: 1px solid #00FF41;
                    selection-background-color: #008F11;
                    selection-color: black;
                    color: #00FF41;
                }
                QTextEdit, QListWidget {
                    background-color: rgba(5, 10, 5, 0.9);
                    border: 1px solid rgba(0, 255, 65, 0.3);
                    border-radius: 6px;
                    color: #00FF41;
                    font-family: 'Courier New', monospace;
                }
                QScrollBar:vertical {
                    border: none;
                    background: black;
                    width: 10px;
                }
                QScrollBar::handle:vertical {
                    background: #00FF41;
                    border-radius: 5px;
                }
            """
        },
        "Cyberpunk Theme": {
            "accent": "#FF007F",
            "bg_gradient": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a0826, stop:1 #080f1d)",
            "glass_card": "rgba(25, 10, 45, 0.7)",
            "border": "rgba(255, 0, 127, 0.4)",
            "text": "#00F0FF",
            "subtext": "#FF007F",
            "qss": """
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a0826, stop:1 #080f1d);
                    color: #00F0FF;
                    font-family: 'Outfit', 'Inter', sans-serif;
                }
                QTabWidget::pane {
                    border: 2px solid #FF007F;
                    border-radius: 16px;
                    background: rgba(25, 10, 45, 0.6);
                }
                QTabBar::tab {
                    background: rgba(15, 5, 30, 0.9);
                    color: #FF007F;
                    border: 1px solid #FF007F;
                    border-bottom: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    margin-right: 4px;
                }
                QTabBar::tab:selected {
                    background: rgba(25, 10, 45, 0.7);
                    color: #00F0FF;
                    border: 2px solid #00F0FF;
                    border-bottom: none;
                }
                QTabBar::tab:hover {
                    color: #00F0FF;
                    background: rgba(100, 10, 80, 0.3);
                }
                QGroupBox {
                    border: 2px solid rgba(0, 240, 255, 0.4);
                    border-radius: 12px;
                    margin-top: 1.5em;
                    font-weight: bold;
                    color: #FF007F;
                    padding: 12px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 5px 0 5px;
                }
                QPushButton {
                    background-color: rgba(255, 0, 127, 0.2);
                    color: #FF007F;
                    border: 2px solid #FF007F;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #FF007F;
                    color: #ffffff;
                    border: 2px solid #00F0FF;
                }
                QPushButton:pressed {
                    background-color: #00F0FF;
                    color: #000000;
                }
                QCheckBox {
                    color: #00F0FF;
                    spacing: 6px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border: 2px solid #FF007F;
                    border-radius: 4px;
                    background-color: #1a0826;
                }
                QCheckBox::indicator:checked {
                    background-color: #00F0FF;
                    border: 2px solid #00F0FF;
                }
                QLabel {
                    color: #00F0FF;
                }
                QSlider::groove:horizontal {
                    border: 2px solid rgba(255, 0, 127, 0.3);
                    height: 10px;
                    background: #1a0826;
                    border-radius: 5px;
                }
                QSlider::handle:horizontal {
                    background: #00F0FF;
                    border: 2px solid #FF007F;
                    width: 18px;
                    margin: -4px 0;
                    border-radius: 9px;
                }
                QComboBox {
                    background-color: #1a0826;
                    border: 2px solid #FF007F;
                    border-radius: 6px;
                    padding: 6px;
                    color: #00F0FF;
                }
                QComboBox QAbstractItemView {
                    background-color: #1a0826;
                    border: 2px solid #00F0FF;
                    selection-background-color: #FF007F;
                    selection-color: white;
                    color: #00F0FF;
                }
                QTextEdit, QListWidget {
                    background-color: rgba(15, 5, 25, 0.8);
                    border: 2px solid rgba(0, 240, 255, 0.3);
                    border-radius: 8px;
                    color: #00F0FF;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #1a0826;
                    width: 12px;
                }
                QScrollBar::handle:vertical {
                    background: #FF007F;
                    border-radius: 6px;
                }
            """
        },
        "Jarvis Theme": {
            "accent": "#00d2ff",
            "bg_gradient": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #040d1a, stop:1 #0c1c38)",
            "glass_card": "rgba(10, 28, 56, 0.7)",
            "border": "rgba(0, 210, 255, 0.4)",
            "text": "#00d2ff",
            "subtext": "#0072ff",
            "qss": """
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #040d1a, stop:1 #0c1c38);
                    color: #00d2ff;
                    font-family: 'Outfit', 'Segoe UI', sans-serif;
                }
                QTabWidget::pane {
                    border: 1px solid rgba(0, 210, 255, 0.4);
                    border-radius: 12px;
                    background: rgba(10, 28, 56, 0.65);
                }
                QTabBar::tab {
                    background: rgba(5, 15, 35, 0.9);
                    color: #0072ff;
                    border: 1px solid rgba(0, 210, 255, 0.3);
                    border-bottom: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    padding: 8px 18px;
                    font-weight: bold;
                    margin-right: 3px;
                }
                QTabBar::tab:selected {
                    background: rgba(10, 28, 56, 0.7);
                    color: #00d2ff;
                    border: 1px solid #00d2ff;
                    border-bottom: none;
                }
                QTabBar::tab:hover {
                    color: #00d2ff;
                    background: rgba(0, 114, 255, 0.2);
                }
                QGroupBox {
                    border: 1px solid rgba(0, 210, 255, 0.4);
                    border-radius: 8px;
                    margin-top: 1.5em;
                    font-weight: bold;
                    color: #00d2ff;
                    padding: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 4px 0 4px;
                }
                QPushButton {
                    background-color: rgba(0, 114, 255, 0.15);
                    color: #00d2ff;
                    border: 1px solid #00d2ff;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00d2ff;
                    color: #040d1a;
                }
                QPushButton:pressed {
                    background-color: #0072ff;
                    color: white;
                }
                QCheckBox {
                    color: #00d2ff;
                    spacing: 6px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 1px solid #00d2ff;
                    border-radius: 9px; /* Circular checkbox looks HUD-like */
                    background-color: #040d1a;
                }
                QCheckBox::indicator:checked {
                    background-color: #00d2ff;
                }
                QLabel {
                    color: #00d2ff;
                }
                QSlider::groove:horizontal {
                    border: 1px solid rgba(0, 210, 255, 0.3);
                    height: 6px;
                    background: #040d1a;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    background: #00d2ff;
                    border: 1px solid #0072ff;
                    width: 14px;
                    height: 14px;
                    margin: -4px 0;
                    border-radius: 7px;
                }
                QComboBox {
                    background-color: #040d1a;
                    border: 1px solid #00d2ff;
                    border-radius: 4px;
                    padding: 5px;
                    color: #00d2ff;
                }
                QComboBox QAbstractItemView {
                    background-color: #040d1a;
                    border: 1px solid #00d2ff;
                    selection-background-color: #0072ff;
                    selection-color: white;
                    color: #00d2ff;
                }
                QTextEdit, QListWidget {
                    background-color: rgba(5, 15, 30, 0.85);
                    border: 1px solid rgba(0, 210, 255, 0.3);
                    border-radius: 6px;
                    color: #00d2ff;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #040d1a;
                    width: 8px;
                }
                QScrollBar::handle:vertical {
                    background: #0072ff;
                    border-radius: 4px;
                }
            """
        },
        "Minimal Theme": {
            "accent": "#ffffff",
            "bg_gradient": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #121212, stop:1 #242424)",
            "glass_card": "rgba(30, 30, 30, 0.85)",
            "border": "rgba(255, 255, 255, 0.15)",
            "text": "#ffffff",
            "subtext": "#aaaaaa",
            "qss": """
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #121212, stop:1 #242424);
                    color: #ffffff;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                }
                QTabWidget::pane {
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 8px;
                    background: rgba(30, 30, 30, 0.8);
                }
                QTabBar::tab {
                    background: rgba(20, 20, 20, 0.8);
                    color: #888888;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: rgba(30, 30, 30, 0.85);
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-bottom: none;
                }
                QTabBar::tab:hover {
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 6px;
                    margin-top: 1.5em;
                    color: #ffffff;
                    padding: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.05);
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 4px;
                    padding: 6px 14px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.15);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.25);
                }
                QCheckBox {
                    color: #ffffff;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 3px;
                    background-color: #121212;
                }
                QCheckBox::indicator:checked {
                    background-color: #ffffff;
                    border: 1px solid #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QSlider::groove:horizontal {
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    height: 4px;
                    background: #121212;
                    border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: #ffffff;
                    width: 12px;
                    margin: -4px 0;
                    border-radius: 6px;
                }
                QComboBox {
                    background-color: #121212;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 4px;
                    padding: 4px;
                    color: #ffffff;
                }
                QComboBox QAbstractItemView {
                    background-color: #121212;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    selection-background-color: rgba(255, 255, 255, 0.1);
                    selection-color: white;
                    color: #ffffff;
                }
                QTextEdit, QListWidget {
                    background-color: rgba(20, 20, 20, 0.85);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                    color: #ffffff;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #121212;
                    width: 6px;
                }
                QScrollBar::handle:vertical {
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 3px;
                }
            """
        }
    }

    @classmethod
    def GetStylesheet(cls, theme_name):
        theme = cls.THEMES.get(theme_name, cls.THEMES["Jarvis Theme"])
        return theme["qss"]

    @classmethod
    def GetThemeMeta(cls, theme_name):
        return cls.THEMES.get(theme_name, cls.THEMES["Jarvis Theme"])
