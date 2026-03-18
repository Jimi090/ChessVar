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
import chess

class SidePanel(QWidget):
    new_game_requested = Signal()
    back_to_menu_requested = Signal()
    previous_move_requested = Signal()
    next_move_requested = Signal()
    export_fen_requested = Signal()
    export_pgn_requested = Signal()
    history_jump_requested = Signal(int)
    pocket_piece_selected = Signal(int)
    pocket_selection_cleared = Signal()

    POCKET_PIECE_LABELS = {
        chess.PAWN: "P",
        chess.KNIGHT: "N",
        chess.BISHOP: "B",
        chess.ROOK: "R",
        chess.QUEEN: "Q",
    }

    def __init__(self, game=None):
        super().__init__()
        self.game = game
        self.pocket_buttons = {}

        self.setFixedWidth(320)
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

        self.pocket_label = QLabel("Reserve:")
        self.pocket_label.setWordWrap(True)
        layout.addWidget(self.pocket_label)

        pocket_layout = QHBoxLayout()
        for piece_type, label in self.POCKET_PIECE_LABELS.items():
            button = QPushButton(label)
            button.setCheckable(True)
            button.setFixedHeight(34)
            button.clicked.connect(
                lambda checked, pt=piece_type: self._handle_pocket_button(pt, checked)
            )
            pocket_layout.addWidget(button)
            self.pocket_buttons[piece_type] = button
        layout.addLayout(pocket_layout)

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

        self.set_pocket_pieces({}, False, None)

    def _handle_pocket_button(self, piece_type, checked):
        if checked:
            for other_piece_type, button in self.pocket_buttons.items():
                if other_piece_type != piece_type:
                    button.blockSignals(True)
                    button.setChecked(False)
                    button.blockSignals(False)
            self.pocket_piece_selected.emit(piece_type)
            return

        self.pocket_selection_cleared.emit()

    def on_history_click(self, item: QListWidgetItem):
        ply_index = item.data(Qt.UserRole)
        if ply_index is not None:
            self.history_jump_requested.emit(ply_index)

    def set_current_player(self, player: str):
        self.current_player_label.setText(f"Current Turn: {player}")

    def set_material_advantage(self, text: str):
        self.material_label.setText(text)

    def set_pocket_pieces(self, counts, enabled, selected_piece):
        if not enabled:
            self.pocket_label.setText("Reserve: unavailable in this variant")
            for button in self.pocket_buttons.values():
                button.blockSignals(True)
                button.setChecked(False)
                button.setEnabled(False)
                button.setText(button.text().split(" ", 1)[0])
                button.blockSignals(False)
            return

        self.pocket_label.setText("Reserve: choose a piece to drop on the board")
        for piece_type, button in self.pocket_buttons.items():
            count = counts.get(piece_type, 0)
            button.blockSignals(True)
            button.setText(f"{self.POCKET_PIECE_LABELS[piece_type]} ({count})")
            button.setEnabled(count > 0)
            button.setChecked(selected_piece == piece_type and count > 0)
            button.blockSignals(False)

    def clear_pocket_selection(self):
        for button in self.pocket_buttons.values():
            button.blockSignals(True)
            button.setChecked(False)
            button.blockSignals(False)

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

