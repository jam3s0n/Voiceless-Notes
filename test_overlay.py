import sys
from PyQt6.QtWidgets import QApplication
from note_overlay import NoteOverlay

app = QApplication(sys.argv)

window = NoteOverlay()
window.show()

sys.exit(app.exec())
