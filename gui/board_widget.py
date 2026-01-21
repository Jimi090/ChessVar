from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt

class ChessBoardWidget(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.square_size = 80
        self.draw_board()

    def draw_board(self):
        colors = [Qt.white,Qt.black]

        for row in range(8):
            for col in range(8):
                color = colors[(row+col) % 2]
                self.scene.addRect(
                    col * self.square_size,
                    row * self.square_size,
                    self.square_size,
                    self.square_size,
                    brush=color,
                )