import time
import threading
from modules.base_module import GestureModule

try:
    import psutil
except Exception:
    pass

class SysInfoModule(GestureModule):
    def __init__(self, name, description, config_manager, ui_callback=None):
        super().__init__(name, description, config_manager)
        self.ui_callback = ui_callback # Updates the floating stats panel
        self.running = False
        self.thread = None
        self.update_interval = 1.0 # Update statistics every 1.0 second
        self.fps_counter = 0
        self.fps_start_time = 0.0
        self.current_fps = 0.0

    def on_enable(self):
        self.running = True
        self.fps_start_time = time.time()
        self.fps_counter = 0
        self.current_fps = 0.0
        # Start a background polling thread for system metrics
        self.thread = threading.Thread(target=self.metrics_loop, daemon=True)
        self.thread.start()

    def on_disable(self):
        self.running = False
        if self.ui_callback:
            self.ui_callback(None)

    def process_hand_landmarks(self, hands_data, frame_size):
        # We record hand frames to calculate actual processing FPS
        self.fps_counter += 1
        curr_time = time.time()
        elapsed = curr_time - self.fps_start_time
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = curr_time

    def metrics_loop(self):
        while self.running:
            try:
                # Gather stats using psutil
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory().percent
                
                battery_percent = 100
                battery_plugged = True
                battery = psutil.sensors_battery()
                if battery:
                    battery_percent = battery.percent
                    battery_plugged = battery.power_plugged

                current_profile = self.config_manager.Get("active_profile", "Normal")

                metrics = {
                    "cpu": cpu,
                    "ram": ram,
                    "battery": battery_percent,
                    "plugged": battery_plugged,
                    "fps": round(self.current_fps, 1),
                    "profile": current_profile
                }

                if self.ui_callback and self.running:
                    self.ui_callback(metrics)
            except Exception as e:
                self.logger.error(f"Error gathering system metrics: {e}")
                
            time.sleep(self.update_interval)
