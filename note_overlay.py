
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from pathlib import Path


class NoteOverlay(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SilentNotes")
        self.resize(450, 350)

        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setWindowOpacity(0.65)

        layout = QVBoxLayout()

        title = QLabel("SilentNotes - Lecture Notes")
        layout.addWidget(title)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Your notes will appear here..."
        )
        layout.addWidget(self.editor)

        save_button = QPushButton("Save Notes")
        save_button.clicked.connect(self.save_notes)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def new_line(self):
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText("\n")
        self.editor.setTextCursor(cursor)

    def insert_important(self):
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText("IMPORTANT: ")
        self.editor.setTextCursor(cursor)

    def undo(self):
        self.editor.undo()

    def save_notes(self):
        path = Path("notes.txt")
        path.write_text(
            self.editor.toPlainText(),
            encoding="utf-8"
        )
        print(f"Notes saved to {path.resolve()}")
