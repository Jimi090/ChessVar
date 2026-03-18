from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt
from gui.variant_rules_dialog import VariantRulesDialog

class MainMenu(QWidget):
    VARIANT_RULES = {
        "Standard": (
            "Classic chess rules apply. Checkmate the opposing king to win.\n\n"
            "• Normal castling, en passant and promotion are enabled.\n"
            "• Stalemate, repetition and move-count draws behave as in regular chess."
        ),
        "Suicide": (
            "The goal is to get rid of all your pieces. If you have no legal move, that also counts as a win.\n\n"
            "• Capturing is mandatory whenever a capture is available.\n"
            "• Check and checkmate do not matter in this variant."
        ),
        "Giveaway": (
            "Giveaway follows the same spirit as Suicide: lose all your pieces before your opponent does.\n\n"
            "• Captures are compulsory.\n"
            "• Kings have no royal status, so check is ignored."
        ),
        "Antichess": (
            "Antichess is another losing-chess variant where you try to get rid of all your pieces first.\n\n"
            "• If a capture is available, you must capture.\n"
            "• The king is treated like an ordinary piece, without check restrictions."
        ),
        "Atomic": (
            "Captures cause an explosion that removes the capturing piece, the captured piece and every adjacent non-pawn piece.\n\n"
            "• Kings may not move into explosion range.\n"
            "• You win by exploding the opposing king."
        ),
        "King of the Hill": (
            "Standard chess rules apply, but there is an extra victory condition.\n\n"
            "• Bring your king to one of the four central squares (d4, e4, d5, e5) to win.\n"
            "• Checkmate is still a valid way to win as well."
        ),
        "Horde": (
            "White starts with a large horde of pawns, while Black has the normal setup.\n\n"
            "• White wins by overwhelming Black.\n"
            "• Black wins by eliminating the entire horde."
        ),
        "Three-check": (
            "Standard chess rules apply, but each side also tracks delivered checks.\n\n"
            "• The first player to give three checks wins immediately.\n"
            "• Checkmate can still end the game earlier."
        ),
    }

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
            QPushButton#RulesButton {
                background-color: transparent;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                font-size: 12px;
                font-weight: normal;
                color: #b8b8b8;
                padding: 5px 10px;
            }
            QPushButton#RulesButton:hover {
                background-color: #242424;
                border-color: #4a4a4a;
                color: #e0e0e0;
            }
            QPushButton#RulesButton:pressed {
                background-color: #1d1d1d;
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
        self.variant_combo.addItems(list(self.VARIANT_RULES.keys()))

        self.variant_rules_btn = QPushButton("Rules")
        self.variant_rules_btn.setObjectName("RulesButton")
        self.variant_rules_btn.setCursor(Qt.PointingHandCursor)
        self.variant_rules_btn.clicked.connect(self.show_variant_rules)

        variant_header = QHBoxLayout()
        variant_header.setSpacing(10)
        variant_header.addWidget(variant_label)
        variant_header.addStretch()
        variant_header.addWidget(self.variant_rules_btn)

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

        self.mode_combo.currentTextChanged.connect(self.update_bot_visibility)

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

        layout.addLayout(variant_header)
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

    def show_variant_rules(self):
        variant_name = self.variant_combo.currentText()
        rules_text = self.VARIANT_RULES.get(
            variant_name,
            "Rules for this variant are not available yet.",
        )
        dialog = VariantRulesDialog(variant_name, rules_text, self)
        dialog.exec()

