import os
import sys
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QCheckBox, QComboBox, QSlider, QLineEdit,
    QFileDialog, QListWidget, QGroupBox, QAbstractItemView, QApplication,
    QSystemTrayIcon
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QImage, QPixmap, QFont, QCloseEvent

from settings.config_manager import ConfigManager
from profiles.profile_manager import ProfileManager
from themes.theme_manager import ThemeManager
from core.camera_thread import CameraThread
from core.module_manager import ModuleManager
from ui.overlays import HUDOverlay, LaserPointerCanvas, WritingCanvas, SystemInfoWidget
from ui.system_tray import SystemTrayManager

logger = logging.getLogger("GestureX.Dashboard")

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GestureX")
        self.setMinimumSize(960, 680)
        self.resize(1000, 720)
        
        # Core structures
        self.config = ConfigManager()
        self.profiles = ProfileManager(self.config)
        self.modules = ModuleManager(self.config)
        self.modules.InitializeModules()
        
        # Load profile configurations
        active_profile = self.config.Get("active_profile", "Normal")
        self.profiles.LoadProfile(active_profile)
        
        # Window attributes
        self.camera_thread = None
        self.is_closing = False
        
        self.InitOverlays()
        self.InitUI()
        self.InitTray()
        
        # Connect Module Callbacks to Overlays
        self.HookModuleCallbacks()

        # Startup Cam
        self.ToggleCamera(True)

    def InitOverlays(self):
        self.hud_volume = HUDOverlay("Volume", self.config.Get("theme"))
        self.hud_brightness = HUDOverlay("Brightness", self.config.Get("theme"))
        self.laser_canvas = LaserPointerCanvas()
        self.writing_canvas = WritingCanvas()
        self.sysinfo_widget = SystemInfoWidget(self.config.Get("theme"))

    def HookModuleCallbacks(self):
        self.modules.RegisterCallback("volume", self.hud_volume.UpdateValue)
        self.modules.RegisterCallback("brightness", self.hud_brightness.UpdateValue)
        self.modules.RegisterCallback("screenshot", self.ShowScreenshotNotification)
        self.modules.RegisterCallback("presentation", lambda val: self.laser_canvas.UpdateLaserPos(val[0], val[1]))
        self.modules.RegisterCallback("writing", lambda val: self.writing_canvas.UpdateCanvas(val[0], val[1]))
        self.modules.RegisterCallback("security", self.HandleSecurityAction)
        self.modules.RegisterCallback("sysinfo", self.sysinfo_widget.UpdateMetrics)
        self.modules.RegisterCallback("gaming", lambda val: self.AddLog(f"Gaming Alert: {val}"))
        self.modules.RegisterCallback("voice", lambda val: self.AddLog(f"Voice Assistant: {val}"))

    def InitUI(self):
        # Master Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Glassmorphic Header Card
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.title_label = QLabel("GESTURE X")
        self.title_label.setFont(QFont("Outfit", 20, QFont.Weight.Bold))
        
        self.profile_lbl = QLabel(f"Active Profile: {self.config.Get('active_profile', 'Normal')}")
        self.profile_lbl.setFont(QFont("Outfit", 10))
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.profile_lbl)
        
        self.main_layout.addWidget(self.header)
        
        # Primary Tab Frame
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Tabs
        self.InitTabDashboard()
        self.InitTabModules()
        self.InitTabMappings()
        self.InitTabSettings()
        
        # Load theme QSS
        self.ApplyTheme(self.config.Get("theme", "Jarvis Theme"))

    def ApplyTheme(self, theme_name):
        self.config.Set("theme", theme_name)
        qss = ThemeManager.GetStylesheet(theme_name)
        self.setStyleSheet(qss)
        
        theme_meta = ThemeManager.GetThemeMeta(theme_name)
        accent = theme_meta["accent"]
        self.title_label.setStyleSheet(f"color: {accent};")
        self.profile_lbl.setStyleSheet(f"color: {theme_meta['subtext']};")
        
        # Update overlays style
        self.hud_volume.SetTheme(theme_name)
        self.hud_brightness.SetTheme(theme_name)
        self.sysinfo_widget.SetTheme(theme_name)

    def InitTray(self):
        self.tray_manager = SystemTrayManager(self, self.profiles)
        self.tray_manager.show()

    # ----------------------------------------------------
    # TAB 1: DASHBOARD (CAM + LOGS)
    # ----------------------------------------------------
    def InitTabDashboard(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Left Panel (Camera Canvas View)
        cam_panel = QGroupBox("Camera Feed Skeleton")
        cam_layout = QVBoxLayout(cam_panel)
        
        self.cam_canvas = QLabel("Camera Feed Initializing...")
        self.cam_canvas.setFixedSize(540, 400)
        self.cam_canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cam_canvas.setStyleSheet("border: 1px solid rgba(255, 255, 255, 0.1); background-color: rgba(0,0,0,0.5); border-radius: 8px;")
        
        # Camera options layout
        cam_opts = QHBoxLayout()
        self.cam_switch = QPushButton("Camera Active")
        self.cam_switch.setCheckable(True)
        self.cam_switch.setChecked(True)
        self.cam_switch.clicked.connect(self.OnCameraToggled)
        
        self.cam_selector = QComboBox()
        for idx in range(3): # Support camera index 0, 1, 2
            self.cam_selector.addItem(f"Camera Device {idx}", idx)
        self.cam_selector.setCurrentIndex(self.config.Get("camera_index", 0))
        self.cam_selector.currentIndexChanged.connect(self.OnCameraSelectorChanged)
        
        cam_opts.addWidget(self.cam_switch)
        cam_opts.addWidget(self.cam_selector)
        
        cam_layout.addWidget(self.cam_canvas)
        cam_layout.addLayout(cam_opts)
        
        # Right Panel (Gesture Log Terminal)
        log_panel = QGroupBox("Activity Console Log")
        log_layout = QVBoxLayout(log_panel)
        
        self.log_list = QListWidget()
        self.log_list.setStyleSheet("background-color: black;")
        self.log_list.setFont(QFont("Courier New", 9))
        self.log_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.AddLog("System initialized. GestureX ready.")
        
        log_layout.addWidget(self.log_list)
        
        layout.addWidget(cam_panel, 3)
        layout.addWidget(log_panel, 2)
        
        self.tabs.addTab(tab, "Dashboard")

    # ----------------------------------------------------
    # TAB 2: MODULE SWITCHES PANEL
    # ----------------------------------------------------
    def InitTabModules(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        scroll_container = QWidget()
        scroll_layout = QVBoxLayout(scroll_container)
        
        self.module_checkboxes = {}
        
        group = QGroupBox("Feature Modules Configuration")
        group_layout = QVBoxLayout(group)
        
        # Generate toggle switch cards dynamically for all 12 modules
        for name, module in self.modules.GetModules().items():
            card = QWidget()
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(5, 5, 5, 5)
            
            lbl_layout = QVBoxLayout()
            m_title = QLabel(name)
            m_title.setFont(QFont("Outfit", 11, QFont.Weight.Bold))
            m_desc = QLabel(module.description)
            m_desc.setFont(QFont("Outfit", 9))
            m_desc.setStyleSheet("color: rgba(255,255,255,0.6);")
            lbl_layout.addWidget(m_title)
            lbl_layout.addWidget(m_desc)
            
            cb = QCheckBox("Enable Module")
            cb.setChecked(self.config.IsModuleEnabled(name))
            cb.toggled.connect(lambda checked, n=name: self.OnModuleStateChanged(n, checked))
            self.module_checkboxes[name] = cb
            
            card_layout.addLayout(lbl_layout)
            card_layout.addStretch()
            card_layout.addWidget(cb)
            
            group_layout.addWidget(card)
            
        scroll_layout.addWidget(group)
        layout.addWidget(scroll_container)
        self.tabs.addTab(tab, "Modules")

    # ----------------------------------------------------
    # TAB 3: GESTURE CONFIG & SENSITIVITY MAPPINGS
    # ----------------------------------------------------
    def InitTabMappings(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Sensitivity settings
        sens_group = QGroupBox("Engine Sensitivity Binds")
        sens_layout = QVBoxLayout(sens_group)
        
        # Volume/Brightness Sensitivity
        vol_sens_lbl = QLabel("Pinch Distance Sensitivity (Hysteresis Multiplier)")
        self.sens_slider = QSlider(Qt.Orientation.Horizontal)
        self.sens_slider.setRange(5, 20) # 0.5 to 2.0 scale
        self.sens_slider.setValue(int(self.config.Get("sensitivity", 1.0) * 10))
        self.sens_slider.valueChanged.connect(self.OnSensitivityChanged)
        sens_layout.addWidget(vol_sens_lbl)
        sens_layout.addWidget(self.sens_slider)
        sens_layout.addSpacing(15)
        
        # Mouse cursor speed
        mouse_speed_lbl = QLabel("Air Mouse Speed Multiplier")
        self.mouse_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.mouse_speed_slider.setRange(5, 30) # 0.5 to 3.0 scale
        self.mouse_speed_slider.setValue(int(self.config.Get("air_mouse_speed", 1.5) * 10))
        self.mouse_speed_slider.valueChanged.connect(self.OnMouseSpeedChanged)
        sens_layout.addWidget(mouse_speed_lbl)
        sens_layout.addWidget(self.mouse_speed_slider)
        
        layout.addWidget(sens_group)
        layout.addStretch()
        self.tabs.addTab(tab, "Mappings")

    # ----------------------------------------------------
    # TAB 4: GENERAL SETTINGS, PROFILES & WINDOW OPTIONS
    # ----------------------------------------------------
    def InitTabSettings(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Theme/Visual Panel
        visual_group = QGroupBox("Theme Preferences")
        visual_layout = QHBoxLayout(visual_group)
        
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Jarvis Theme", "Matrix Theme", "Cyberpunk Theme", "Minimal Theme"])
        self.theme_dropdown.setCurrentText(self.config.Get("theme", "Jarvis Theme"))
        self.theme_dropdown.currentTextChanged.connect(self.ApplyTheme)
        
        visual_layout.addWidget(QLabel("Visual Styles Selector"))
        visual_layout.addWidget(self.theme_dropdown)
        layout.addWidget(visual_group)
        
        # Folder Path setup
        folder_group = QGroupBox("Screenshots Target Folder")
        folder_layout = QHBoxLayout(folder_group)
        
        self.folder_input = QLineEdit()
        self.folder_input.setText(self.config.Get("screenshot_folder", "screenshots"))
        self.folder_input.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.OnBrowseScreenshotFolder)
        
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_btn)
        layout.addWidget(folder_group)
        
        # Profiles control
        profile_group = QGroupBox("Profiles Loader")
        profile_layout = QHBoxLayout(profile_group)
        
        self.profile_dropdown = QComboBox()
        self.profile_dropdown.addItems(self.profiles.ListProfiles())
        self.profile_dropdown.setCurrentText(self.config.Get("active_profile", "Normal"))
        
        load_prof_btn = QPushButton("Load Profile")
        load_prof_btn.clicked.connect(self.OnLoadProfileClicked)
        
        import_prof_btn = QPushButton("Import Profile...")
        import_prof_btn.clicked.connect(self.OnImportProfile)
        
        profile_layout.addWidget(QLabel("Select Active Profile:"))
        profile_layout.addWidget(self.profile_dropdown)
        profile_layout.addWidget(load_prof_btn)
        profile_layout.addWidget(import_prof_btn)
        layout.addWidget(profile_group)

        # Boot options & security registration
        boot_group = QGroupBox("Windows Startup & Security Features")
        boot_layout = QVBoxLayout(boot_group)
        
        self.startup_cb = QCheckBox("Start GestureX automatically with Windows")
        self.startup_cb.setChecked(self.config.Get("startup_with_windows", False))
        self.startup_cb.toggled.connect(self.OnStartupToggled)
        
        self.reg_face_btn = QPushButton("Register Owner Face Landmarks Profile")
        self.reg_face_btn.clicked.connect(self.OnRegisterFaceClicked)
        
        self.reset_btn = QPushButton("Reset App Configurations to Defaults")
        self.reset_btn.setStyleSheet("color: red; border: 1px solid red;")
        self.reset_btn.clicked.connect(self.OnResetToDefaults)

        boot_layout.addWidget(self.startup_cb)
        boot_layout.addWidget(self.reg_face_btn)
        boot_layout.addSpacing(10)
        boot_layout.addWidget(self.reset_btn)
        
        layout.addWidget(boot_group)
        layout.addStretch()
        self.tabs.addTab(tab, "Settings")

    # ----------------------------------------------------
    # CAMERA CONTROLS
    # ----------------------------------------------------
    def ToggleCamera(self, active):
        if active:
            cam_idx = self.config.Get("camera_index", 0)
            self.camera_thread = CameraThread(cam_idx)
            self.camera_thread.frame_ready.connect(self.OnFrameReady)
            self.camera_thread.hands_detected.connect(self.modules.ProcessHandLandmarks)
            self.camera_thread.face_detected.connect(self.modules.ProcessFaceLandmarks)
            self.camera_thread.status_message.connect(self.AddLog)
            self.camera_thread.start()
        else:
            if self.camera_thread:
                self.camera_thread.stop()
                self.camera_thread = None
            self.cam_canvas.setText("Camera Stream Stopped")

    def OnCameraToggled(self):
        active = self.cam_switch.isChecked()
        self.ToggleCamera(active)
        self.cam_switch.setText("Camera Active" if active else "Camera Stopped")

    def OnCameraSelectorChanged(self, idx):
        self.config.Set("camera_index", idx)
        # Restart camera stream using new index
        if self.cam_switch.isChecked():
            self.ToggleCamera(False)
            self.ToggleCamera(True)

    def OnFrameReady(self, q_img):
        # Resize image cleanly to match QLabel dimensions
        pix = QPixmap.fromImage(q_img)
        scaled_pix = pix.scaled(self.cam_canvas.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.cam_canvas.setPixmap(scaled_pix)

    # ----------------------------------------------------
    # CONFIGURATION & SETTINGS CHANGE CALLBACKS
    # ----------------------------------------------------
    def OnModuleStateChanged(self, module_name, enabled):
        self.config.SetModuleSetting(module_name, "enabled", enabled)
        self.modules.RefreshModuleStates()
        self.AddLog(f"Module '{module_name}' set to {'ENABLED' if enabled else 'DISABLED'}")

    def OnSensitivityChanged(self, value):
        sens = value / 10.0
        self.config.Set("sensitivity", sens)
        # Update settings across enabled modules
        self.modules.RefreshModuleStates()

    def OnMouseSpeedChanged(self, value):
        speed = value / 10.0
        self.config.Set("air_mouse_speed", speed)
        # Update air mouse speeds dynamically
        mouse_module = self.modules.GetModules().get("Air Mouse")
        if mouse_module:
            mouse_module.mouse_speed = speed

    def OnBrowseScreenshotFolder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Folder to Save Screenshots", self.folder_input.text())
        if dir_path:
            self.folder_input.setText(dir_path)
            self.config.Set("screenshot_folder", dir_path)
            self.AddLog(f"Screenshot folder updated to: {dir_path}")

    def OnStartupToggled(self, checked):
        self.config.Set("startup_with_windows", checked)
        from utils.sys_utils import ToggleStartup
        ToggleStartup(checked)

    def OnRegisterFaceClicked(self):
        # Setting owner face ratio back to None triggers registration in Security Module on the next face mesh pass
        self.config.Set("owner_face_ratio", None)
        security_mod = self.modules.GetModules().get("Security Module")
        if security_mod:
            security_mod.owner_face_ratio = None
        self.AddLog("Face registration requested. Please look directly into the camera.")

    def LoadProfileByName(self, profile_name):
        success = self.profiles.LoadProfile(profile_name)
        if success:
            self.config.Set("active_profile", profile_name)
            self.profile_lbl.setText(f"Active Profile: {profile_name}")
            self.profile_dropdown.setCurrentText(profile_name)
            
            # Sync Checkboxes & Styling
            for name, cb in self.module_checkboxes.items():
                cb.setChecked(self.config.IsModuleEnabled(name))
            
            self.theme_dropdown.setCurrentText(self.config.Get("theme", "Jarvis Theme"))
            self.ApplyTheme(self.config.Get("theme", "Jarvis Theme"))
            
            # Reapply modules configuration
            self.modules.RefreshModuleStates()
            
            # Update mappings sliders
            self.sens_slider.setValue(int(self.config.Get("sensitivity", 1.0) * 10))
            self.mouse_speed_slider.setValue(int(self.config.Get("air_mouse_speed", 1.5) * 10))
            
            self.AddLog(f"Profile '{profile_name}' applied successfully.")
            return True
        return False

    def OnLoadProfileClicked(self):
        profile = self.profile_dropdown.currentText()
        self.LoadProfileByName(profile)

    def OnImportProfile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import User Profile JSON File", "", "JSON Files (*.json)")
        if file_path:
            success = self.profiles.ImportProfile(file_path)
            if success:
                # Refresh dropdown items
                self.profile_dropdown.clear()
                self.profile_dropdown.addItems(self.profiles.ListProfiles())
                self.AddLog(f"Profile imported from: {os.path.basename(file_path)}")
            else:
                self.AddLog("Failed to import profile: Invalid structure.")

    def OnResetToDefaults(self):
        self.config.ResetToDefaults()
        self.LoadProfileByName("Normal")
        self.AddLog("All configuration settings reset to system defaults.")

    # ----------------------------------------------------
    # UI ALERTS AND OVERLAYS ROUTING
    # ----------------------------------------------------
    def AddLog(self, message):
        self.log_list.addItem(message)
        self.log_list.scrollToBottom()
        # Keep log size limited
        if self.log_list.count() > 100:
            self.log_list.takeItem(0)

    def ShowScreenshotNotification(self, filepath):
        self.AddLog(f"Screenshot Saved: {os.path.basename(filepath)}")
        # Dynamic system notification
        from PyQt6.QtWidgets import QMessageBox
        # Let's show a sleek floating notification or just a tray message (standard on Windows)
        self.tray_manager.showMessage(
            "Screenshot Saved Successfully",
            f"Saved to: {os.path.basename(filepath)}",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def HandleSecurityAction(self, event_data):
        action, value = event_data
        if action == "PRIVACY_BLUR":
            # Enable transparent full screen blur or solid color overlay window
            if value:
                self.AddLog("Security Alert: Privacy Mode Activated.")
                # Paint writing canvas overlay solid dark translucent color to hide screen content
                self.writing_canvas.UpdateCanvas([], "PRIVACY MODE ACTIVE (SCREEN BLURRED)")
            else:
                self.AddLog("Security Alert: Privacy Mode Deactivated.")
                self.writing_canvas.UpdateCanvas(None, "")
        elif action == "FACE_REGISTERED":
            self.AddLog(f"Security: Owner Face Registered! {value}")
        elif action == "INTRUDER_ALERT":
            self.AddLog(f"INTRUDER WARNING! Snapshot: {os.path.basename(value)}")
            self.tray_manager.showMessage(
                "SECURITY WARNING",
                "Intruder face detected! Frame captured.",
                QSystemTrayIcon.MessageIcon.Warning,
                4000
            )

    # ----------------------------------------------------
    # SYSTEM CLOSE AND TERMINATE EVENTS
    # ----------------------------------------------------
    def closeEvent(self, event: QCloseEvent):
        # Override Close to minimize utility to tray instead of quitting
        if not self.is_closing:
            event.ignore()
            self.hide()
            self.tray_manager.showMessage(
                "GestureX minimized to System Tray",
                "Double-click tray icon to show dashboard again.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            if self.tray_manager.contextMenu():
                self.tray_manager.toggle_action.setText("Show Dashboard")
        else:
            self.ToggleCamera(False)
            # Hide overlays
            self.hud_volume.close()
            self.hud_brightness.close()
            self.laser_canvas.close()
            self.writing_canvas.close()
            self.sysinfo_widget.close()
            event.accept()

    def QuitApplication(self):
        self.is_closing = True
        self.close()
        QApplication.quit()
