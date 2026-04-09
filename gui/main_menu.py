from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QHBoxLayout, QToolButton, QMenu
)
from PySide6.QtCore import Qt, Signal
from gui.variant_rules_dialog import VariantRulesDialog

class MainMenu(QWidget):
    section_selected = Signal(str)
    VARIANT_RULES = {
        "Standard": (
            "Classic chess rules: checkmate the opposing king to win.\n\n"
            "How it plays:\n"
            "• Tactical and strategic balance between opening, middlegame and endgame.\n"
            "• The king must stay safe, and tempo/development matter from move one.\n\n"
            "Important rules:\n"
            "• Castling, en passant and promotion are enabled.\n"
            "• Draws by stalemate, repetition, insufficient material and move-count rules apply."
        ),
        "Suicide": (
            "The goal is to lose all your own pieces first.\n\n"
            "How it plays:\n"
            "• You often sacrifice valuable pieces on purpose.\n"
            "• Positioning to force your opponent to take can be stronger than direct attacks.\n\n"
            "Important rules:\n"
            "• Capturing is mandatory whenever any capture is available.\n"
            "• Check/checkmate do not matter; the king is not royal.\n"
            "• If you have no legal move, that counts as a win."
        ),
        "Atomic": (
            "Every capture explodes.\n\n"
            "How it plays:\n"
            "• Capturing becomes both attack and self-destruct mechanism.\n"
            "• King safety is very different: proximity to any capturable square is dangerous.\n\n"
            "Important rules:\n"
            "• A capture removes the capturing piece, captured piece, and adjacent non-pawn pieces.\n"
            "• Kings cannot move into explosion range.\n"
            "• You win by exploding the opponent king."
        ),
        "King of the Hill": (
            "Standard chess + race for the center.\n\n"
            "How it plays:\n"
            "• King activity is a real weapon, not only an endgame idea.\n"
            "• Central control and safe king routes become top priorities.\n\n"
            "Important rules:\n"
            "• Reach d4, e4, d5 or e5 with your king to win instantly.\n"
            "• Checkmate is still a normal win condition."
        ),
        "Giveaway": (
            "A losing-chess variant where you try to get rid of your army.\n\n"
            "How it plays:\n"
            "• Material advantage can be bad, because extra pieces are extra liabilities.\n"
            "• Piece traps and forced capture sequences decide many games.\n\n"
            "Important rules:\n"
            "• Captures are compulsory.\n"
            "• The king has no royal status and check is ignored."
        ),
        "Horde": (
            "Asymmetrical battle: White has a pawn horde, Black has regular pieces.\n\n"
            "How it plays:\n"
            "• White relies on space and numbers.\n"
            "• Black relies on coordination, tactical breaks and king safety.\n\n"
            "Important rules:\n"
            "• White wins by surviving and overwhelming Black's army.\n"
            "• Black wins by eliminating the entire horde."
        ),
        "Antichess": (
            "A pure forcing variant focused on mandatory captures.\n\n"
            "How it plays:\n"
            "• Tempo and move-order are everything.\n"
            "• Quiet-looking positions can hide forced tactical lines many moves long.\n\n"
            "Important rules:\n"
            "• If a capture exists, you must capture.\n"
            "• The king is an ordinary piece; check restrictions do not apply.\n"
            "• First side to lose all pieces wins."
        ),
        "Three-check": (
            "Standard chess with an extra tactical win condition.\n\n"
            "How it plays:\n"
            "• Initiative and king harassment are often stronger than material grabs.\n"
            "• Sacrifices to force repeated checks are common.\n\n"
            "Important rules:\n"
            "• Deliver three checks to win immediately.\n"
            "• Checkmate is still valid and can end the game before the third check."
        ),
    }
    SHORTCUTS_TEXT = (
        "Keyboard shortcuts during the game:\n\n"
        "• ← : previous move in history\n"
        "• → : next move in history\n"
        "• Home : jump to initial position\n"
        "• End : jump to latest position\n"
        "• Ctrl+N : start new game\n"
        "• Ctrl+M : back to main menu\n"
        "• Ctrl+S : export PGN"
    )

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
                font-family: Arial;
            }
            QLabel#Title {
                font-size: 52px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#Subtitle {
                font-size: 22px;
                color: #b8b8b8;
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

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(14, 14, 14, 14)
        page_layout.setSpacing(8)

        top_bar = QHBoxLayout()
        self.menu_button = QToolButton()
        self.menu_button.setText("☰")
        self.menu_button.setToolTip("Menu")
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.setPopupMode(QToolButton.InstantPopup)
        self.menu_button.setStyleSheet("""
                    QToolButton {
                        background-color: #1e1e1e;
                        border: 1px solid #333;
                        border-radius: 8px;
                        font-size: 22px;
                        color: #e0e0e0;
                        padding: 3px 10px;
                    }
                    QToolButton:hover {
                        background-color: #2a2a2a;
                    }
                """)

        menu = QMenu(self)
        menu.setStyleSheet("""
                    QMenu {
                        background-color: #1e1e1e;
                        border: 1px solid #333333;
                        border-radius: 8px;
                        padding: 6px;
                    }
                    QMenu::item {
                        color: #e0e0e0;
                        font-size: 18px;
                        padding: 10px 18px;
                        border-radius: 6px;
                    }
                    QMenu::item:selected {
                        background-color: #2e4a25;
                        color: #ffffff;
                    }
                """)
        play_action = menu.addAction("Play Game")
        puzzle_action = menu.addAction("Chess Puzzles")
        play_action.triggered.connect(lambda: self.section_selected.emit("game"))
        puzzle_action.triggered.connect(lambda: self.section_selected.emit("puzzle"))
        self.menu_button.setMenu(menu)

        top_bar.addWidget(self.menu_button, alignment=Qt.AlignLeft | Qt.AlignTop)
        top_bar.addStretch(1)
        page_layout.addLayout(top_bar)

        root = QHBoxLayout()
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(20)

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
        layout.setSpacing(0)

        title = QLabel("ChessVar")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Choose your game")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

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

        # -------- SIDE --------
        side_label = QLabel("Play as")
        side_label.setProperty("class", "section")

        self.side_combo = QComboBox()
        self.side_combo.addItems(["White", "Black"])

        # -------- BOT DIFFICULTY --------
        self.bot_label = QLabel("Bot Difficulty")
        self.bot_label.setProperty("class", "section")

        self.bot_combo = QComboBox()
        self.bot_combo.addItems([
            "Beginner",
            "Novice",
            "Intermediate",
            "Advanced",
            "Master",
        ])
        self.bot_combo.setCurrentText("Intermediate")

        self.mode_combo.currentTextChanged.connect(self.update_bot_visibility)

        self.update_bot_visibility()

        start_btn = QPushButton("Start Game")
        start_btn.setFixedHeight(48)
        small_gap=8
        big_gap=20

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(big_gap)

        layout.addWidget(mode_label)
        layout.addSpacing(small_gap)
        layout.addWidget(self.mode_combo)
        layout.addSpacing(big_gap)

        layout.addWidget(variant_label)
        layout.addSpacing(small_gap)
        layout.addWidget(self.variant_combo)
        layout.addSpacing(big_gap)
        layout.addWidget(side_label)
        layout.addSpacing(small_gap)
        layout.addWidget(self.side_combo)
        layout.addSpacing(big_gap)

        layout.addWidget(self.bot_label)
        layout.addSpacing(small_gap)
        layout.addWidget(self.bot_combo)
        layout.addSpacing(big_gap)

        layout.addSpacing(6)
        layout.addWidget(start_btn)

        side_buttons = QVBoxLayout()
        side_buttons.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        side_buttons.setSpacing(14)

        self.variant_rules_btn = QPushButton("Rules")
        self.variant_rules_btn.setObjectName("RulesButton")
        self.variant_rules_btn.setCursor(Qt.PointingHandCursor)
        self.variant_rules_btn.clicked.connect(self.show_variant_rules)

        self.shortcuts_btn = QPushButton("Shortcuts")
        self.shortcuts_btn.setObjectName("RulesButton")
        self.shortcuts_btn.setCursor(Qt.PointingHandCursor)
        self.shortcuts_btn.clicked.connect(self.show_shortcuts)

        side_buttons.addWidget(self.variant_rules_btn)
        side_buttons.addWidget(self.shortcuts_btn)

        root.addWidget(card)
        root.addSpacing(8)
        root.addLayout(side_buttons)
        page_layout.addLayout(root, stretch=1)

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

    def show_shortcuts(self):
        dialog = VariantRulesDialog("Shortcuts", self.SHORTCUTS_TEXT, self)
        dialog.exec()
