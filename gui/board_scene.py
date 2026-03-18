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

        self.annotation_start = None
        self.annotation_dragged = False

    def scene_pos_to_board_square(self, scene_pos):
        return self.board.scene_pos_to_board_square(scene_pos)

    def mousePressEvent(self, event):
        pos = event.scenePos()

        if event.button() == Qt.LeftButton and (self.board.highlighted_squares or self.board.arrows):
            self.board.clear_annotations()

        if event.button() == Qt.RightButton:
            square = self.scene_pos_to_board_square(pos)
            if square is not None:
                self.annotation_start = square
                self.annotation_dragged = False
                event.accept()
                return
        size = self.board.square_size

        col = int(pos.x() // size)
        row = 7 - int(pos.y() // size)
        if(self.board.game.player_pov == "Black"):
            col=7-col
            row=7-row
        item = self.itemAt(pos, self.views()[0].transform())

        if event.button() == Qt.LeftButton and self.board.selected_drop_piece is not None and not isinstance(item, PieceItem):
            if self.board.drop_piece(col, row):
                event.accept()
                return

        if isinstance(item, PieceItem):
            if self.board.selected_piece and item.piece != self.board.selected_piece:
                if self.board.move_piece(self.board.selected_piece, col, row):
                    self.board.selected_piece = None
                    self.board.clear_legal_move_markers()
                else:
                    self.board.select_piece(item.piece)
                event.accept()
                return
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
            self.board.clear_legal_move_markers()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.annotation_start is not None and event.buttons() & Qt.RightButton:
            self.annotation_dragged = True
            event.accept()
            return

        if self.drag_item:
            self.drag_started = True
            self.drag_item.setPos(event.scenePos() + self.drag_offset)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.annotation_start is not None:
            end_square = self.board.scene_pos_to_board_square(event.scenePos())
            if end_square is not None:
                if self.annotation_dragged and end_square != self.annotation_start:
                    self.board.toggle_arrow(self.annotation_start, end_square)
                else:
                    self.board.toggle_square_highlight(end_square)

            self.annotation_start = None
            self.annotation_dragged = False
            event.accept()
            return

        if self.drag_item and self.drag_started:
            self.board.on_piece_dropped(self.drag_item, event.scenePos())

        self.drag_item = None
        self.drag_offset = None
        self.drag_started = False

        super().mouseReleaseEvent(event)