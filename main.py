import chess.variant
from gui.main_window import MainWindow
from game.game import GameState
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStatusBar, QApplication
)
import sys


app=QApplication(sys.argv)
game=GameState(chess,"normal")
main_window=MainWindow()
main_window.board.render_position(chess.Board.board_fen(game.board))

main_window.show()
app.exec()
