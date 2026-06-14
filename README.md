# GestureX - Control Beyond Touch

GestureX is a futuristic, modular, and plugin-based Windows desktop utility that allows you to control your system using hand gestures captured by a standard webcam. It is built using Python, PyQt6, OpenCV, and MediaPipe.

---

## 🌟 Key Features

GestureX works with a **modular architecture** where features act as independent plugin modules. 

### Core Modules (Enabled by Default)
*   🔊 **Volume Control (LEFT Hand)**: Pinch thumb and index finger closer to lower system volume; spread wide to increase.
*   🔆 **Brightness Control (RIGHT Hand)**: Pinch thumb and index finger to dim screen brightness; spread wide to increase.
*   📸 **Screenshot Gesture (Any Hand)**: Transition from an **Open Palm** to a **Closed Fist** to capture and save a timestamped screenshot in `screenshots/`.

### Optional Modules (Toggleable in Settings)
*   🖱️ **Air Mouse**: Move the cursor using your index finger; pinch thumb-index to Left Click, thumb-middle to Right Click, and index-middle up/down to scroll.
*   🎵 **Media Controls**: Swipe left/right to skip tracks, hold a Thumb-Up to Play/Pause.
*   🚀 **Application Launcher**: Form static hand shapes (like a "V-sign" or "Horns") to open VS Code, Chrome, Spotify, or Steam.
*   📊 **System Info Widget**: Draggable, glassmorphic widget displaying CPU, Memory, Battery, and processing FPS in real-time.
*   🛡️ **Security Module**: Lock your PC instantly by raising both palms, toggle Privacy Mode (screen blur + mic mute) by holding five fingers for 3 seconds, and record intruder snapshots.
*   📝 **Air Writing**: Draw in the air with your index finger, perform OCR, and export the recognized text straight to your clipboard.
*   🎙️ **Voice Assistant**: Hold open palm for 2 seconds to launch a voice command listener (supports "Open Browser", "Open Calculator", etc.).
*   📽️ **Presentation Mode**: Swipe right/left to navigate slides, and use an open palm to project a red laser pointer tracking your index finger.

---

## 🎨 Futuristic Themes
Customize GestureX to match your style:
1.  **Jarvis Theme**: Holographic tech-blue design.
2.  **Matrix Theme**: Dark green scrolling terminal font.
3.  **Cyberpunk Theme**: Neon pink and cyan glow.
4.  **Minimal Theme**: Flat monochromatic aesthetic.

---

## 🚀 How to Download and Run

Visitors to your repository can download and run GestureX in two ways:

### Option 1: Downloading Pre-Compiled Releases (For End-Users)
Once you compile the application into a standalone executable (e.g., using PyInstaller), visitors can download the file from the **Releases** section on GitHub and run it directly without installing Python:
1.  Go to the **Releases** section on the right side of this GitHub page.
2.  Download `GestureX.exe`.
3.  Double-click to run!

### Option 2: Running from Source (For Developers)

#### Prerequisites
*   Python 3.10 to 3.14
*   A working Webcam

#### Installation Steps
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/cyberpranit/GestureX.git
    cd GestureX
    ```
2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
3.  **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the application**:
    ```bash
    python main.py
    ```

---

## 🔧 Building the Standalone Executable (`.exe`)

To build the `GestureX.exe` file that visitors can download and run without Python:

1.  Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Compile the project:
    ```bash
    pyinstaller --noconsole --onefile --name=GestureX --add-data "core/hand_landmarker.task;core" --add-data "core/face_landmarker.task;core" main.py
    ```
3.  The compiled executable will be saved inside the `dist/` directory as `GestureX.exe`. You can upload this file to the **Releases** section of your GitHub repository.
