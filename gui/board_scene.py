from PySide6.QtWidgets import QGraphicsScene
from gui.piece_item import PieceItem
from PySide6.QtCore import Qt, QPointF

class BoardScene(QGraphicsScene):
    def __init__(self, board_widget):
        super().__init__()
        self.board = board_widget

        self.drag_item = None
        self.drag_offset = QPointF()
        self.drag_started = False

    def mousePressEvent(self, event):
        pos = event.scenePos()
        size = self.board.square_size

        col = int(pos.x() // size)
        row = 7 - int(pos.y() // size)
        if(self.board.game.player_pov == "Black"):
            col=7-col
            row=7-row
        item = self.itemAt(pos, self.views()[0].transform())

        if isinstance(item, PieceItem) and not self.board.selected_piece:
            self.board.select_piece(item.piece)
            self.drag_item = item
            self.drag_offset = item.pos() - pos
            self.drag_started = False

            event.accept()
            return

        if self.board.selected_piece:
            self.board.move_piece(
                self.board.selected_piece,
                col,
                row
            )
            self.board.selected_piece = None
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_item:
            self.drag_started = True
            self.drag_item.setPos(event.scenePos() + self.drag_offset)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drag_item and self.drag_started:
            self.board.on_piece_dropped(self.drag_item, event.scenePos())

        self.drag_item = None
        self.drag_offset = None
        self.drag_started = False

        super().mouseReleaseEvent(event)