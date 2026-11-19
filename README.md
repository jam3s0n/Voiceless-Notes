
# SilentNotes

### Hands-Free Note-Taking Using Computer Vision

SilentNotes is a Python desktop application that enables users to control a note-taking interface through silent mouth gestures. By combining real-time facial landmark tracking with gesture-recognition algorithms, SilentNotes translates predefined mouth movements into text-editing commands without requiring speech or keyboard input.

The project explores computer vision, human-computer interaction, and alternative input methods for desktop applications.

## Features

- **Real-Time Gesture Recognition:** Detects mouth movements using facial landmarks.
- **Hands-Free Text Editing:** Converts predefined mouth gestures into note-editing commands.
- **Floating Note Editor:** Provides a semi-transparent, always-on-top note-taking window.
- **Live Webcam Preview:** Displays the webcam feed and gesture-tracking information.
- **Personalized Calibration:** Calibrates the user's neutral mouth width for horizontal gesture detection.
- **Local Note Saving:** Saves notes to a `.txt` file.
- **Multithreaded Processing:** Runs webcam processing in a separate thread to maintain a responsive GUI.

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Core application logic |
| OpenCV | Webcam capture and image processing |
| MediaPipe | Facial landmark detection and tracking |
| PyQt6 | Desktop GUI and thread communication |
| NumPy | Numerical calculations |

## Supported Gestures

SilentNotes currently recognizes three mouth gestures.

| Gesture | Action | Description |
|---------|--------|-------------|
| Hold Mouth Open | New Line | Hold your mouth open for at least 600 ms to insert a new line. |
| Double Mouth Pulse | Important | Open and close your mouth twice quickly to insert `IMPORTANT:`. |
| Horizontal Lip Stretch | Undo | Hold a wide smile for at least 400 ms to undo the previous edit. |

Gesture recognition uses configurable thresholds and timing requirements to distinguish intentional commands from ordinary facial movements.

## How It Works

SilentNotes uses a real-time computer vision pipeline to process facial movements and execute commands.

1. **Video Capture:** OpenCV captures video frames from the user's webcam.
2. **Facial Landmark Detection:** MediaPipe Face Mesh identifies facial landmarks, including points around the mouth.
3. **Feature Extraction:** The application calculates the Mouth Aspect Ratio (MAR) and horizontal lip-stretch ratio.
4. **Gesture Classification:** A rule-based state machine evaluates mouth movement, timing, and threshold conditions.
5. **Command Execution:** Recognized gestures trigger editing actions in the PyQt6 note-taking interface.

### Mouth Aspect Ratio (MAR)

The Mouth Aspect Ratio measures vertical mouth opening relative to horizontal mouth width.

MAR = Vertical Lip Distance / Horizontal Mouth Width

The application uses MediaPipe landmarks:

- **13:** Upper inner lip
- **14:** Lower inner lip
- **61:** Left mouth corner
- **291:** Right mouth corner

A larger MAR indicates a more open mouth.

### Horizontal Lip-Stretch Ratio

The lip-stretch ratio measures how much the mouth widens compared to its neutral position.

Stretch Ratio = Current Mouth Width / Calibrated Neutral Mouth Width

During startup, SilentNotes calibrates the user's neutral mouth width over approximately three seconds.

This measurement is used to detect intentional horizontal mouth stretching.

### Gesture Timing

SilentNotes combines geometric measurements with timing conditions.

For example:

- A sustained mouth opening triggers a new line.
- Two short mouth-opening pulses trigger the important-text command.
- A sustained horizontal stretch triggers undo.

Separate activation and release thresholds help prevent repeated triggering when measurements fluctuate near a threshold.

## Installation

### Prerequisites

- Python 3.11
- A working webcam
- Windows 11 (development environment)
- Git (optional)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/SilentNotes.git
cd SilentNotes
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install mediapipe==0.10.21 opencv-python numpy PyQt6
```

### 4. Run the Application

```bash
python main.py
```

## Usage

1. Run the application.
2. Position your face clearly in front of the webcam.
3. Keep your mouth relaxed during the initial calibration period.
4. Use the floating editor to type notes normally.
5. Perform the supported mouth gestures to execute editing commands.
6. Click **Save Notes** to save your notes to `notes.txt`.

### Exiting the Application

- **Close the notes window:** Exits the application and stops webcam processing.
- **Press Q in the webcam preview:** Stops webcam tracking while leaving the notes window open.

## Project Structure

```text
SilentNotes/
├── main.py
├── gesture_detector.py
├── note_overlay.py
├── test_overlay.py
├── README.md
└── .gitignore
```

### File Descriptions

- **main.py:** Initializes the application and connects gesture signals to editing commands.
- **gesture_detector.py:** Handles webcam capture, facial landmark processing, calibration, and gesture recognition.
- **note_overlay.py:** Implements the floating PyQt6 note-taking interface.
- **test_overlay.py:** Provides standalone testing for the note-taking GUI.

## Technical Design

### Facial Landmark Tracking

MediaPipe Face Mesh detects facial landmarks in each processed frame. The application extracts mouth coordinates to calculate geometric measurements.

### Rule-Based Gesture Recognition

Rather than training a custom gesture-classification model, SilentNotes uses configurable thresholds and a timing-based state machine.

This approach provides interpretable gesture rules and allows detection parameters to be adjusted without retraining a model.

### Multithreaded Architecture

Webcam processing runs in a PyQt6 `QThread`, separate from the main GUI thread.

When a gesture is recognized, the detector emits a signal that is handled by the note-taking interface.

This separation helps keep the application responsive during continuous video processing.

### Local Processing

Facial landmark detection and gesture recognition run locally on the user's computer. The application does not require a cloud-based recognition service.

## Future Improvements

- Evaluate gesture-recognition accuracy using structured testing.
- Reduce response latency and unintended gesture activations.
- Support customizable gesture-to-command mappings.
- Add additional text-editing and formatting commands.
- Improve detection under different lighting conditions and camera angles.
- Add automatic note saving.
- Package SilentNotes as a standalone desktop executable.

## Project Status

**Working Prototype**

SilentNotes currently supports three predefined mouth gestures, real-time webcam tracking, a floating note-taking interface, and local text-file saving.

Development is ongoing, with a focus on improving gesture accuracy, responsiveness, and usability.
