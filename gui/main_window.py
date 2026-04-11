from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtGui import QKeySequence, QShortcut
from gui.main_menu import MainMenu
from gui.game_widget import GameWidget
from gui.puzzle_widget import PuzzleWidget
from game.game import GameState
import chess
import chess.variant

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ChessVar")
        self.resize(1000, 700)
        self._setup_window_shortcuts()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu = MainMenu()
        self.stack.addWidget(self.menu)

        self.menu.start_btn.clicked.connect(self.start_game)
        self.menu.section_selected.connect(self.handle_section_selected)
        self.puzzle_widget = None

    def _setup_window_shortcuts(self):
        self.fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        self.fullscreen_shortcut.activated.connect(self.toggle_fullscreen)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

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

    def handle_section_selected(self, section):
        if section == "puzzle":
            self.show_puzzle_mode()
        else:
            self.show_main_menu()

    def show_puzzle_mode(self):
        if self.puzzle_widget is None:
            self.puzzle_widget = PuzzleWidget(navigate_callback=self.handle_section_selected)
            self.stack.addWidget(self.puzzle_widget)
        self.stack.setCurrentWidget(self.puzzle_widget)

    def show_main_menu(self):
        self.stack.setCurrentWidget(self.menu)
