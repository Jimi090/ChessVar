from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, QSize, Signal

class SidePanel(QWidget):
    new_game_requested = Signal()
    back_to_menu_requested = Signal()
    previous_move_requested = Signal()
    next_move_requested = Signal()
    export_fen_requested = Signal()
    export_pgn_requested = Signal()
    history_jump_requested = Signal(int)


    def __init__(self, game=None):
        super().__init__()
        self.game = game

        self.setMinimumWidth(250)
        self.setMaximumWidth(460)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(12)

        self.back_to_menu_btn = QPushButton("Main Menu")
        self.back_to_menu_btn.setFixedHeight(38)
        layout.addWidget(self.back_to_menu_btn)

        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.setFixedHeight(38)
        layout.addWidget(self.new_game_btn)

        self.current_player_label = QLabel("Current Turn: White")
        self.current_player_label.setAlignment(Qt.AlignCenter)
        self.current_player_label.setStyleSheet("font-weight: bold; font-size: 13pt;")
        layout.addWidget(self.current_player_label)

        self.material_label = QLabel("Material: Equal")
        self.material_label.setWordWrap(True)
        layout.addWidget(self.material_label)

        layout.addWidget(QLabel("Move History:"))
        self.move_list = QListWidget()
        self.move_list.setFixedHeight(260)
        layout.addWidget(self.move_list)

        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("◀")
        self.next_btn = QPushButton("▶")
        self.prev_btn.setFixedSize(QSize(55, 30))
        self.next_btn.setFixedSize(QSize(55, 30))
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

        export_label = QLabel("Export game:")
        layout.addWidget(export_label)

        export_layout = QHBoxLayout()
        self.export_fen_btn = QPushButton("Export FEN")
        self.export_pgn_btn = QPushButton("Export PGN")
        export_layout.addWidget(self.export_fen_btn)
        export_layout.addWidget(self.export_pgn_btn)
        layout.addLayout(export_layout)

        layout.addStretch()

        self.move_list.itemClicked.connect(self.on_history_click)
        self.back_to_menu_btn.clicked.connect(self.back_to_menu_requested.emit)
        self.new_game_btn.clicked.connect(self.new_game_requested.emit)
        self.prev_btn.clicked.connect(self.previous_move_requested.emit)
        self.next_btn.clicked.connect(self.next_move_requested.emit)
        self.export_fen_btn.clicked.connect(self.export_fen_requested.emit)
        self.export_pgn_btn.clicked.connect(self.export_pgn_requested.emit)
        self._apply_scaling(self.width())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_scaling(event.size().width())

    def _apply_scaling(self, width):
        scale = max(0.85, min(1.35, width / 320))
        button_height = int(38 * scale)
        nav_width = int(55 * scale)
        nav_height = int(30 * scale)
        move_history_height = int(260 * scale)

        self.back_to_menu_btn.setFixedHeight(button_height)
        self.new_game_btn.setFixedHeight(button_height)
        self.prev_btn.setFixedSize(QSize(nav_width, nav_height))
        self.next_btn.setFixedSize(QSize(nav_width, nav_height))
        self.move_list.setMinimumHeight(max(180, move_history_height))
        self.move_list.setMaximumHeight(int(360 * scale))

        title_size = int(13 * scale)
        body_size = int(11 * scale)
        self.current_player_label.setStyleSheet(f"font-weight: bold; font-size: {title_size}pt;")
        self.material_label.setStyleSheet(f"font-size: {body_size}pt;")

    def on_history_click(self, item: QListWidgetItem):
        ply_index = item.data(Qt.UserRole)
        if ply_index is not None:
            self.history_jump_requested.emit(ply_index)

    def set_current_player(self, player: str):
        self.current_player_label.setText(f"Current Turn: {player}")

    def set_material_advantage(self, text: str):
        self.material_label.setText(text)

    def set_move_history(self, moves_with_ply, selected_ply):
        self.move_list.clear()
        for label, ply in moves_with_ply:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, ply)
            self.move_list.addItem(item)
            if ply == selected_ply:
                item.setSelected(True)
                self.move_list.scrollToItem(item)

        has_moves = len(moves_with_ply) > 0
        self.prev_btn.setEnabled(has_moves and selected_ply > 0)
        self.next_btn.setEnabled(has_moves and selected_ply < len(moves_with_ply))

