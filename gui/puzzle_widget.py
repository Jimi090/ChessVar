import csv
import json
import random
from pathlib import Path
import chess
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QToolButton,
    QMenu,
)

from game.game import GameState
from gui.board_widget import ChessBoardWidget
from utils.path_utils import resource_path


class PuzzleWidget(QWidget):
    PROGRESS_FILE = Path.home() / ".chessvar" / "puzzle_progress.json"

    def __init__(self, navigate_callback=None):
        super().__init__()
        self.navigate_callback = navigate_callback
        self.puzzles = self._load_puzzles()
        self.current_index = None
        self.current_puzzle = None
        self.current_index = 0
        self.expected_move = None
        self.solver_color = "White"
        self.solved_ids = self._load_progress()
        self.pending_puzzle_indices = []

        self.game = GameState(chess, "standard")
        self.game.vs_bot = False
        self.board_widget = ChessBoardWidget(self.game)
        self.board_widget.preserve_pov_on_move = True
        self.board_widget.move_played.connect(self._on_move_played)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(14, 14, 14, 14)
        page_layout.setSpacing(8)

        top_bar = QHBoxLayout()
        self.menu_button = QToolButton()
        self.menu_button.setText("☰")
        self.menu_button.setToolTip("Menu")
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.setPopupMode(QToolButton.InstantPopup)
        self.menu_button.setStyleSheet("""
            QToolButton {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
                font-size: 22px;
                color: #e0e0e0;
                padding: 3px 10px;
            }
            QToolButton:hover {
                background-color: #2a2a2a;
            }
        """)

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                color: #e0e0e0;
                font-size: 18px;
                padding: 10px 18px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #2e4a25;
                color: #ffffff;
            }
        """)
        play_action = menu.addAction("Play Game")
        puzzle_action = menu.addAction("Chess Puzzles")
        history_action = menu.addAction("Game History")
        play_action.triggered.connect(lambda: self._navigate("game"))
        puzzle_action.triggered.connect(lambda: self._navigate("puzzle"))
        history_action.triggered.connect(lambda: self._navigate("history"))
        self.menu_button.setMenu(menu)

        top_bar.addWidget(self.menu_button, alignment=Qt.AlignLeft | Qt.AlignTop)
        top_bar.addStretch(1)
        page_layout.addLayout(top_bar)

        content = QHBoxLayout()
        content.setSpacing(18)
        content.setAlignment(Qt.AlignCenter)
        page_layout.addLayout(content, stretch=1)

        content.addWidget(self.board_widget, stretch=3, alignment=Qt.AlignVCenter)

        self.right_panel = QFrame()
        self.right_panel.setMinimumWidth(260)
        self.right_panel.setMaximumWidth(420)
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: #1b1b1b;
                border-radius: 16px;
            }
            QLabel#PanelTitle {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#PanelMeta {
                font-size: 14px;
                color: #b8b8b8;
            }
            QLabel#StatusLabel {
                font-size: 15px;
                color: #d8d8d8;
            }
            QPushButton {
                background-color: #769656;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                color: white;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #8fbf72;
            }
            QPushButton:pressed {
                background-color: #5c7f45;
            }
            QPushButton:disabled {
                background-color: #3f4f35;
                color: #b9b9b9;
            }
        """)

        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(18, 18, 18, 18)
        right_layout.setSpacing(10)

        title = QLabel("Chess Puzzles")
        title.setObjectName("PanelTitle")
        title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(title)

        self.counter_label = QLabel("")
        self.counter_label.setObjectName("PanelMeta")
        self.counter_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.counter_label)

        self.perspective_label = QLabel("")
        self.perspective_label.setObjectName("PanelMeta")
        self.perspective_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.perspective_label)

        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.status_label)

        right_layout.addSpacing(8)
        self.hint_btn = QPushButton("Hint")
        self.solution_btn = QPushButton("Show Solution")
        self.next_btn = QPushButton("Next Puzzle")
        self.back_btn = QPushButton("Back to Main Menu")

        self.next_btn.setEnabled(False)
        self.hint_btn.clicked.connect(self._show_hint)
        self.solution_btn.clicked.connect(self._show_solution)
        self.next_btn.clicked.connect(self._next_puzzle)
        self.back_btn.clicked.connect(lambda: self._navigate("game"))

        right_layout.addWidget(self.hint_btn)
        right_layout.addWidget(self.solution_btn)
        right_layout.addWidget(self.next_btn)
        right_layout.addWidget(self.back_btn)
        right_layout.addStretch(1)

        content.addWidget(self.right_panel, stretch=2, alignment=Qt.AlignTop)

        self._refresh_pending_puzzles()
        if self.pending_puzzle_indices:
            self._advance_puzzle(load_first=True)
        else:
            self.status_label.setText("No unsolved puzzles available.")
            self.board_widget.interaction_enabled = False
            self.hint_btn.setEnabled(False)
            self.solution_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
        self._apply_scaling(self.width())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_scaling(event.size().width())

    def _apply_scaling(self, width):
        scale = max(0.85, min(1.35, width / 1200))
        panel_width = int(width * 0.22)
        self.right_panel.setFixedWidth(max(260, min(420, panel_width)))
        button_height = int(44 * scale)
        button_font_size = max(11, int(16 * scale))
        menu_btn_font_size = max(18, int(28 * scale))
        menu_btn_padding_v = max(5, int(6 * scale))
        menu_btn_padding_h = max(12, int(16 * scale))
        menu_btn_radius = max(10, int(12 * scale))
        for button in (self.hint_btn, self.solution_btn, self.next_btn, self.back_btn):
            button.setMinimumHeight(button_height)
            button.setFont(QFont("Arial", button_font_size, QFont.Bold))
        self.menu_button.setFont(QFont("Arial", menu_btn_font_size))
        self.menu_button.setStyleSheet(f"""
            QToolButton {{
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: {menu_btn_radius}px;
                font-size: {menu_btn_font_size}px;
                color: #e0e0e0;
                padding: {menu_btn_padding_v}px {menu_btn_padding_h}px;
            }}
            QToolButton:hover {{
                background-color: #2a2a2a;
            }}
        """)

    def _navigate(self, section):
        if self.navigate_callback:
            self.navigate_callback(section)

    def _load_puzzles(self):
        puzzle_path = Path(resource_path("puzzles/chess_puzzles.csv"))
        puzzles = []
        if not puzzle_path.exists():
            return puzzles

        with puzzle_path.open("r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                moves = (row.get("Moves") or "").strip().split()
                if not moves:
                    continue
                puzzles.append({"id": len(puzzles), "fen": row.get("FEN", ""), "solution": moves[0]})
        return puzzles

    def _load_progress(self):
        if not self.PROGRESS_FILE.exists():
            return set()
        try:
            with self.PROGRESS_FILE.open("r", encoding="utf-8") as progress_file:
                payload = json.load(progress_file)
        except (json.JSONDecodeError, OSError):
            return set()
        solved = payload.get("solved_ids", [])
        return {int(item) for item in solved if str(item).isdigit()}

    def _save_progress(self):
        try:
            self.PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with self.PROGRESS_FILE.open("w", encoding="utf-8") as progress_file:
                json.dump({"solved_ids": sorted(self.solved_ids)}, progress_file)
        except OSError:
            pass

    def _refresh_pending_puzzles(self):
        self.pending_puzzle_indices = [i for i, puzzle in enumerate(self.puzzles) if puzzle["id"] not in self.solved_ids]
        random.shuffle(self.pending_puzzle_indices)

    def _load_current_puzzle(self):
        if self.current_index is None:
            return
        puzzle = self.puzzles[self.current_index]
        self.current_puzzle = puzzle
        self.expected_move = puzzle["solution"]

        self.game.board = chess.Board(puzzle["fen"])
        self.solver_color = "White" if self.game.board.turn == chess.WHITE else "Black"
        self.game.player_pov = self.solver_color
        self.game.is_first_move = False

        self.board_widget.interaction_enabled = True
        self.board_widget.interaction_block_reason = None
        self.board_widget.clear_annotations()
        self.board_widget.render_position(self.game.get_display_fen(), self.game.player_pov)

        solved_count = len(self.solved_ids)
        remaining_count = len(self.pending_puzzle_indices)
        self.counter_label.setText(
            f"Solved: {solved_count} / {len(self.puzzles)} | Remaining: {remaining_count}"
        )
        self.perspective_label.setText(f"Solve from: {self.solver_color}")
        self.status_label.setStyleSheet("font-size: 15px; color: #d8d8d8;")
        self.status_label.setText("Find the best move. Only the correct move solves this puzzle.")
        self.next_btn.setEnabled(False)

    def _on_move_played(self):
        if not self.game.board.move_stack:
            return

        played_move = self.game.board.move_stack[-1].uci()
        if played_move == self.expected_move:
            self.board_widget.interaction_enabled = False
            self.board_widget.interaction_block_reason = "solved"
            if self.current_puzzle is not None:
                self.solved_ids.add(self.current_puzzle["id"])
                self._save_progress()
            self.status_label.setStyleSheet("font-size: 15px; color: #8fd16a;")
            self.status_label.setText("Correct! Click 'Next Puzzle' to continue.")
            self.next_btn.setEnabled(True)
            return

        self.game.board.pop()
        self.game.player_pov = self.solver_color
        self.board_widget.interaction_enabled = True
        self.board_widget.interaction_block_reason = None
        self.board_widget.clear_annotations()
        self.board_widget.render_position(self.game.get_display_fen(), self.game.player_pov)
        self.status_label.setStyleSheet("font-size: 15px; color: #ff8a8a;")
        self.status_label.setText("That move is not correct for this puzzle. Try again.")

    def _solution_move(self):
        return chess.Move.from_uci(self.expected_move)

    def _show_hint(self):
        if not self.expected_move:
            return
        solution_move = self._solution_move()
        from_square = solution_move.from_square
        from_col = chess.square_file(from_square)
        from_row = chess.square_rank(from_square)
        self.board_widget.clear_annotations()
        self.board_widget.toggle_square_highlight((from_col, from_row))
        self.status_label.setStyleSheet("font-size: 15px; color: #f4d06f;")
        self.status_label.setText("Hint: Move the highlighted piece.")

    def _show_solution(self):
        if not self.expected_move:
            return
        solution_move = self._solution_move()
        start = (
            chess.square_file(solution_move.from_square),
            chess.square_rank(solution_move.from_square),
        )
        end = (
            chess.square_file(solution_move.to_square),
            chess.square_rank(solution_move.to_square),
        )
        self.board_widget.clear_annotations()
        self.board_widget.toggle_square_highlight(start)
        self.board_widget.toggle_arrow(start, end)
        self.status_label.setStyleSheet("font-size: 15px; color: #f4d06f;")
        self.status_label.setText(f"Solution move: {self.expected_move}")

    def _next_puzzle(self):
        self._advance_puzzle(load_first=False)

    def _advance_puzzle(self, load_first):
        if not self.puzzles:
            return

        if not load_first and self.current_index is not None:
            self.pending_puzzle_indices = [
                index for index in self.pending_puzzle_indices if index != self.current_index
            ]

        if not self.pending_puzzle_indices:
            self.current_index = None
            self.current_puzzle = None
            self.expected_move = None
            self.counter_label.setText(f"Solved: {len(self.solved_ids)} / {len(self.puzzles)}")
            self.perspective_label.setText("Solve from: -")
            self.status_label.setStyleSheet("font-size: 15px; color: #8fd16a;")
            self.status_label.setText("Great job! You solved all available puzzles.")
            self.board_widget.interaction_enabled = False
            self.board_widget.interaction_block_reason = "solved"
            self.hint_btn.setEnabled(False)
            self.solution_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return

        self.current_index = self.pending_puzzle_indices[0]
        self.hint_btn.setEnabled(True)
        self.solution_btn.setEnabled(True)
        self._load_current_puzzle()
