from PySide6.QtWidgets import QGraphicsScene
from gui.piece_item import PieceItem

class BoardScene(QGraphicsScene):
    def __init__(self, board_widget):
        super().__init__()
        self.board = board_widget

    def mousePressEvent(self, event):
        pos = event.scenePos()
        size = self.board.square_size

        col = int(pos.x() // size)
        row = 7 - int(pos.y() // size)

        items = self.items(pos)

        for item in items:

            if isinstance(item, PieceItem) and not self.board.selected_piece:
                self.board.select_piece(item.piece)
                return

        if self.board.selected_piece:
            self.board.move_piece(
                self.board.selected_piece,
                col,
                row
            )
            self.board.selected_piece = None

