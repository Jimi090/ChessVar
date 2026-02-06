from PySide6.QtWidgets import QWidget, QHBoxLayout
from gui.board_widget import ChessBoardWidget
from gui.side_panel import SidePanel
import chess

class GameWidget(QWidget):
    def __init__(self, game):
        super().__init__()

        layout = QHBoxLayout(self)

        self.board = ChessBoardWidget(game)
        self.side_panel = SidePanel(game)

        self.board.render_position(chess.Board.board_fen(game.board), game.player_pov)

        layout.addWidget(self.board, stretch=3)
        layout.addWidget(self.side_panel, stretch=1)
