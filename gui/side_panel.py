from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QSpinBox, QSlider
)
from PySide6.QtCore import Qt, QSize

class SidePanel(QWidget):
    def __init__(self, game=None):
        super().__init__()
        self.game = game  # możesz podpiąć GameState

        self.setFixedWidth(300)  # szerokość panelu
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(15)

        # -------------------- GAME CONTROL --------------------
        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.setFixedHeight(40)
        layout.addWidget(self.new_game_btn)

        # -------------------- CURRENT PLAYER --------------------
        self.current_player_label = QLabel("Current Turn: White")
        self.current_player_label.setAlignment(Qt.AlignCenter)
        self.current_player_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        layout.addWidget(self.current_player_label)

        # -------------------- MATERIAL COUNT --------------------
        self.material_label = QLabel("Material Count:\nWhite: 16  Black: 16")
        self.material_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.material_label)

        # -------------------- MOVE HISTORY --------------------
        layout.addWidget(QLabel("Move History:"))
        self.move_list = QListWidget()
        self.move_list.setFixedHeight(250)
        layout.addWidget(self.move_list)

        # strzałki do poruszania po historii
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("◀")
        self.next_btn = QPushButton("▶")
        self.prev_btn.setFixedSize(QSize(50, 30))
        self.next_btn.setFixedSize(QSize(50, 30))
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

        # eksport historii
        self.export_btn = QPushButton("Export PGN")
        self.export_btn.setFixedHeight(30)
        layout.addWidget(self.export_btn)

        # -------------------- GAME VARIANT --------------------
        layout.addWidget(QLabel("Game Variant:"))
        self.variant_combo = QComboBox()
        self.variant_combo.addItems(["Normal", "Antichess", "Horde", "King of the Hill"])
        layout.addWidget(self.variant_combo)

        # -------------------- AI LEVEL --------------------
        layout.addWidget(QLabel("Bot Difficulty:"))
        self.ai_level_spin = QSpinBox()
        self.ai_level_spin.setRange(1, 10)
        self.ai_level_spin.setValue(3)
        layout.addWidget(self.ai_level_spin)

        # -------------------- TIMER --------------------
        layout.addWidget(QLabel("Timer (optional):"))
        self.timer_slider = QSlider(Qt.Horizontal)
        self.timer_slider.setRange(0, 60)  # w minutach
        self.timer_slider.setValue(10)
        layout.addWidget(self.timer_slider)

        layout.addStretch()

        # -------------------- SIGNALS --------------------
        # kliknięcie na ruch w historii
        self.move_list.itemClicked.connect(self.on_history_click)

    # -------------------- PLACEHOLDER METHODS --------------------
    def on_history_click(self, item: QListWidgetItem):
        print("Clicked move:", item.text())

    # aktualizacja obecnego gracza
    def set_current_player(self, player: str):
        self.current_player_label.setText(f"Current Turn: {player}")

    # aktualizacja materiału
    def set_material_count(self, white: int, black: int):
        self.material_label.setText(f"Material Count:\nWhite: {white}  Black: {black}")

    # dodanie ruchu do historii
    def add_move_to_history(self, move_text: str):
        self.move_list.addItem(move_text)
        self.move_list.scrollToBottom()
