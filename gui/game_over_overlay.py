from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class GameOverOverlay(QWidget):
    def __init__(self, parent, title_text, reason_text):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 160);")
        self.setAttribute(Qt.WA_DeleteOnClose)

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)

        container = QFrame(self)
        container.setFixedSize(440, 280)
        container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 16px;
            }
        """)

        card = QVBoxLayout(container)
        card.setAlignment(Qt.AlignCenter)
        card.setSpacing(25)
        card.setContentsMargins(30, 30, 30, 30)

        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setStyleSheet("color: white;")

        reason = QLabel(reason_text)
        reason.setAlignment(Qt.AlignCenter)
        reason.setFont(QFont("Arial", 16))
        reason.setStyleSheet("color: #cccccc;")

        btn = QPushButton("New Game")
        btn.setFixedSize(200, 48)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #769656;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #8fbf72; }
            QPushButton:pressed { background-color: #5c7f45; }
        """)

        card.addWidget(title)
        card.addWidget(reason)
        card.addStretch()
        card.addWidget(btn, alignment=Qt.AlignCenter)

        root.addWidget(container)
        self.new_game_btn = btn