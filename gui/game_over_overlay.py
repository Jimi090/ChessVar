from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout
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
        card.setSpacing(18)
        card.setContentsMargins(30, 30, 30, 30)

        header_container = QWidget(container)
        header_container.setStyleSheet("""
        QWidget {
        background-color: #2b2b2b;
        }
        """)
        header = QHBoxLayout(header_container)
        header.setContentsMargins(0,0,0,0)
        header.addStretch()

        close_btn = QPushButton("x")
        close_btn.setFixedSize(34,34)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #dddddd;
                border: none;
                border-radius: 17px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4a4a4a; }
            QPushButton:pressed { background-color: #303030; }
        """)
        close_btn.clicked.connect(self.close)
        header.addWidget(close_btn)

        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setStyleSheet("color: white;")

        reason = QLabel(reason_text)
        reason.setAlignment(Qt.AlignCenter)
        reason.setFont(QFont("Arial", 14))
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

        card.addWidget(header_container)
        card.addWidget(title)
        card.addWidget(reason)
        card.addStretch()
        card.addWidget(btn, alignment=Qt.AlignCenter)

        root.addWidget(container)
        self.new_game_btn = btn
        self.close_btn = close_btn