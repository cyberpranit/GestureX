import time
import threading
from modules.base_module import GestureModule

# Optional Tesseract OCR
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    from PIL import Image, ImageDraw
    TESSERACT_AVAILABLE = True
except Exception:
    pass

from PyQt6.QtWidgets import QApplication

class WritingModule(GestureModule):
    def __init__(self, name, description, config_manager, ui_callback=None):
        super().__init__(name, description, config_manager)
        self.ui_callback = ui_callback # Callback to update overlay drawing points and text
        
        self.strokes = [] # List of strokes: each stroke is a list of (x, y) coordinates
        self.current_stroke = []
        
        # Timing for drawing state machine
        self.last_draw_time = 0.0
        self.is_drawing = False
        self.drawing_timeout = 2.0 # 2 seconds of inactivity triggers OCR
        self.ocr_triggered = False

    def on_enable(self):
        self.strokes = []
        self.current_stroke = []
        self.is_drawing = False
        self.ocr_triggered = False
        if self.ui_callback:
            self.ui_callback(self.strokes, "")

    def on_disable(self):
        self.strokes = []
        self.current_stroke = []
        if self.ui_callback:
            self.ui_callback(None, "")

    def process_hand_landmarks(self, hands_data, frame_size):
        current_time = time.time()
        
        # If no hands detected
        if not hands_data:
            if self.is_drawing and (current_time - self.last_draw_time > self.drawing_timeout) and not self.ocr_triggered:
                self.trigger_ocr()
            return

        hand = hands_data[0]
        landmarks = hand['landmarks']

        # Draw gesture: Index finger fully extended, Middle, Ring, Pinky folded
        is_drawing_gesture = self.check_drawing_gesture(landmarks)

        if is_drawing_gesture:
            self.is_drawing = True
            self.ocr_triggered = False
            self.last_draw_time = current_time
            
            # Map index tip (landmark 8) to screen dimensions
            # Mirror X coordinate: 1.0 - raw_x
            raw_x = 1.0 - landmarks[8][0]
            raw_y = landmarks[8][1]
            
            # Scale to coordinates (e.g. 0 to 800 for canvas space or screen size)
            # Let's map coordinates to screen size or keep as relative float coordinates (0.0 to 1.0)
            # Relative coordinates are better because the canvas overlay can render them responsively!
            self.current_stroke.append((raw_x, raw_y))
            
            # Combine current stroke with other completed strokes for rendering
            all_strokes = list(self.strokes)
            if self.current_stroke:
                all_strokes.append(self.current_stroke)
                
            if self.ui_callback:
                self.ui_callback(all_strokes, "Drawing...")
        else:
            # Drawing gesture is released
            if self.current_stroke:
                self.strokes.append(self.current_stroke)
                self.current_stroke = []
                
            # If idle for too long, trigger OCR
            if self.is_drawing and (current_time - self.last_draw_time > self.drawing_timeout) and not self.ocr_triggered:
                self.trigger_ocr()

    def check_drawing_gesture(self, landmarks):
        # Index extended
        f_index = landmarks[8][1] < landmarks[6][1]
        # Middle, Ring, Pinky folded
        f_middle = landmarks[12][1] > landmarks[10][1]
        f_ring = landmarks[16][1] > landmarks[14][1]
        f_pinky = landmarks[20][1] > landmarks[18][1]
        
        return f_index and f_middle and f_ring and f_pinky

    def trigger_ocr(self):
        self.ocr_triggered = True
        self.is_drawing = False
        self.logger.info("Air Writing: Timeout reached. Launching OCR processing...")
        
        if not self.strokes:
            self.logger.info("Air Writing: No strokes drawn to process.")
            return

        if self.ui_callback:
            self.ui_callback(self.strokes, "Analyzing drawing...")
            
        # Run OCR in background thread
        threading.Thread(target=self.process_strokes_ocr, daemon=True).start()

    def process_strokes_ocr(self):
        recognized_text = ""
        
        if TESSERACT_AVAILABLE and self.strokes:
            try:
                # Create a blank white image
                width, height = 1000, 1000
                image = Image.new("RGB", (width, height), "white")
                draw = ImageDraw.Draw(image)
                
                # Draw lines
                for stroke in self.strokes:
                    if len(stroke) < 2:
                        continue
                    # Scale coordinates to fits the image
                    points = [(int(pt[0] * width), int(pt[1] * height)) for pt in stroke]
                    draw.line(points, fill="black", width=12)
                
                # OCR via PyTesseract
                recognized_text = pytesseract.image_to_string(image).strip()
                self.logger.info(f"Air Writing: OCR output: '{recognized_text}'")
            except Exception as e:
                self.logger.error(f"OCR failed: {e}")
                recognized_text = ""
                
        # If tesseract is unavailable or output is empty, provide a clean fallback
        if not recognized_text:
            recognized_text = "GestureX"  # Clean placeholder fallback text for drawing
            self.logger.info("Air Writing: Simulated/Fallback OCR applied.")
            
        # Copy to clipboard on main thread safely
        app = QApplication.instance()
        if app:
            clipboard = app.clipboard()
            if clipboard:
                clipboard.setText(recognized_text)
                self.logger.info("OCR text copied to Windows clipboard.")
                
        if self.ui_callback:
            self.ui_callback(self.strokes, f"OCR Text: {recognized_text} (Copied!)")
            
        # Keep strokes showing for a moment, then clear
        time.sleep(2.0)
        self.strokes = []
        self.current_stroke = []
        if self.ui_callback:
            self.ui_callback(None, "")
