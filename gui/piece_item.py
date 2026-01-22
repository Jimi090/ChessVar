from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


class PieceItem(QGraphicsSvgItem):
    def __init__(self,piece,svg_path):
        super().__init__(svg_path)
        self.piece = piece

        self.setAcceptedMouseButtons(Qt.NoButton)