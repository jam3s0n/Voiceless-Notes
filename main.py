
import sys

from PyQt6.QtWidgets import QApplication
from gesture_detector import GestureDetector
from note_overlay import NoteOverlay


app = QApplication(sys.argv)

# Create note overlay
window = NoteOverlay()
window.show()

# Create webcam gesture detector
detector = GestureDetector()


def handle_gesture(gesture):
    print("Detected:", gesture)

    if gesture == "NEW_LINE":
        window.new_line()

    elif gesture == "IMPORTANT":
        window.insert_important()

    elif gesture == "UNDO":
        window.undo()


# Connect webcam gestures to notes
detector.gesture_detected.connect(handle_gesture)

# Stop webcam when application exits
app.aboutToQuit.connect(detector.stop)

# Start webcam
detector.start()

sys.exit(app.exec())
