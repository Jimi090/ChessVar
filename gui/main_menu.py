from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame
)
from PySide6.QtCore import Qt
class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
                font-family: Arial;
            }
            QLabel#Title {
                font-size: 36px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel.section {
                font-size: 14px;
                color: #bbbbbb;
            }
            QComboBox {
                background-color: #1e1e1e;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #333;
            }
            QPushButton {
                background-color: #769656;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #8fbf72;
            }
            QPushButton:pressed {
                background-color: #5c7f45;
            }
        """)

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedWidth(420)
        card.setStyleSheet("""
            QFrame {
                background-color: #1b1b1b;
                border-radius: 16px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(18)

        title = QLabel("ChessVar")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Choose your game")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #999999;")

        # -------- MODE --------
        mode_label = QLabel("Game Mode")
        mode_label.setProperty("class", "section")

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Player vs Bot",
            "Player vs Player"
        ])

        # -------- VARIANT --------
        variant_label = QLabel("Variant")
        variant_label.setProperty("class", "section")

        self.variant_combo = QComboBox()
        self.variant_combo.addItems([
            "Normal",
            "Atomic",
            "Horde",
            "Antichess",
            "King of the Hill"
        ])

        # -------- SIDE --------
        side_label = QLabel("Play as")
        side_label.setProperty("class", "section")

        self.side_combo = QComboBox()
        self.side_combo.addItems(["White", "Black"])

        # -------- BOT DIFFICULTY --------
        self.bot_label = QLabel("Bot Difficulty")
        self.bot_label.setProperty("class", "section")

        self.bot_combo = QComboBox()
        self.bot_combo.addItems(["Easy", "Medium", "Hard"])

        self.mode_combo.currentTextChanged.connect(
            self.update_bot_visibility
        )

        self.update_bot_visibility()

        start_btn = QPushButton("Start Game")
        start_btn.setFixedHeight(48)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)

        layout.addWidget(mode_label)
        layout.addWidget(self.mode_combo)

        layout.addWidget(variant_label)
        layout.addWidget(self.variant_combo)

        layout.addWidget(side_label)
        layout.addWidget(self.side_combo)

        layout.addWidget(self.bot_label)
        layout.addWidget(self.bot_combo)

        layout.addSpacing(10)
        layout.addWidget(start_btn)

        root.addWidget(card)

        self.start_btn = start_btn

    def update_bot_visibility(self):
        is_bot = "Bot" in self.mode_combo.currentText()
        self.bot_label.setVisible(is_bot)
        self.bot_combo.setVisible(is_bot)
