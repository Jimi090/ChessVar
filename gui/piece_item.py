from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtWidgets import QGraphicsItem

class PieceItem(QGraphicsSvgItem):
    def __init__(self,piece,svg_path):
        super().__init__(svg_path)
        self.piece = piece
        self.drag_start_pos=None

        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)