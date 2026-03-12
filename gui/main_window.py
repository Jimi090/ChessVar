from PySide6.QtWidgets import QMainWindow, QStackedWidget
from gui.main_menu import MainMenu
from gui.game_widget import GameWidget
from game.game import GameState
import chess
import chess.variant

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ChessVar")
        self.resize(1000, 700)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu = MainMenu()
        self.stack.addWidget(self.menu)

        self.menu.start_btn.clicked.connect(self.start_game)

    def start_game(self):
        mode = self.menu.mode_combo.currentText()
        variant_name = self.menu.variant_combo.currentText().lower()
        bot_level = self.menu.bot_combo.currentText()
        selected_side = self.menu.side_combo.currentText()

        game = GameState(chess, variant_name)
        game.vs_bot = "Bot" in mode
        game.bot_level = bot_level
        game.player_pov = selected_side

        self.game_widget = GameWidget(game,back_to_menu_callback=self.show_main_menu)
        self.stack.addWidget(self.game_widget)
        self.stack.setCurrentWidget(self.game_widget)
    def show_main_menu(self):
        self.stack.setCurrentWidget(self.menu)
