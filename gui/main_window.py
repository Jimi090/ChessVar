from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStatusBar, QApplication
)
import sys
from gui.board_widget import ChessBoardWidget
from gui.side_panel import SidePanel

class MainWindow(QMainWindow):
    def __init__(self,game):
        super().__init__()
        self.game = game
        self.setWindowTitle("ChessVar")
        self.resize(1000,700)

        central=QWidget()
        layout = QHBoxLayout(central)

        self.board = ChessBoardWidget(game)
        self.side_panel = SidePanel()

        layout.addWidget(self.board,stretch=3)
        layout.addWidget(self.side_panel,stretch=1)

        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar())
