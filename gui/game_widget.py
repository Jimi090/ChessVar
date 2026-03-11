from PySide6.QtWidgets import QWidget, QHBoxLayout, QFileDialog
from PySide6.QtCore import QSignalBlocker
from gui.board_widget import ChessBoardWidget
from gui.side_panel import SidePanel
import chess
import chess.pgn


class GameWidget(QWidget):
    PIECE_VALUES = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }

    def __init__(self, game, back_to_menu_callback=None):
        super().__init__()

        self.game = game
        self.back_to_menu_callback = back_to_menu_callback
        self.review_index = len(self.game.board.move_stack)

        layout = QHBoxLayout(self)

        self.board = ChessBoardWidget(game)
        self.side_panel = SidePanel(game)

        self.board.render_position(chess.Board.board_fen(game.board), game.player_pov)

        layout.addWidget(self.board, stretch=3)
        layout.addWidget(self.side_panel, stretch=1)

        self.side_panel.new_game_requested.connect(self.start_new_game)
        self.side_panel.back_to_menu_requested.connect(self.back_to_main_menu)
        self.side_panel.previous_move_requested.connect(self.previous_move)
        self.side_panel.next_move_requested.connect(self.next_move)
        self.side_panel.history_jump_requested.connect(self.jump_to_ply)
        self.side_panel.export_fen_requested.connect(self.export_fen)
        self.side_panel.export_pgn_requested.connect(self.export_pgn)
        self.board.move_played.connect(self.on_move_played)

        self.refresh_sidebar()

    def on_move_played(self):
        self.review_index = len(self.game.board.move_stack)
        self.board.interaction_enabled = True
        self.refresh_sidebar()

    def start_new_game(self):
        self.game.board.reset()
        self.game.is_first_move = True
        self.review_index = 0
        self.board.interaction_enabled = True
        self.board.render_position(self.game.board.board_fen(), self.game.player_pov)
        self.refresh_sidebar()

    def back_to_main_menu(self):
        if self.back_to_menu_callback:
            self.back_to_menu_callback()

    def _board_at(self, ply_index):
        board_copy = self.game.board.root()
        for move in self.game.board.move_stack[:ply_index]:
            board_copy.push(move)
        return board_copy

    def _history_rows(self):
        board_for_san = self.game.board.root()
        rows = []

        for index, move in enumerate(self.game.board.move_stack):
            san = board_for_san.san(move)
            move_number = (index // 2) + 1
            if index % 2 == 0:
                label = f"{move_number}. {san}"
            else:
                label = f"{move_number}... {san}"
            rows.append((label, index + 1))
            board_for_san.push(move)
        return rows

    def refresh_sidebar(self):
        current_board = self._board_at(self.review_index)
        current_turn = "White" if current_board.turn == chess.WHITE else "Black"
        self.side_panel.set_current_player(current_turn)
        self.side_panel.set_material_advantage(self._material_text(current_board))

        with QSignalBlocker(self.side_panel.move_list):
            self.side_panel.set_move_history(self._history_rows(), self.review_index)

    def _material_score(self, board, color):
        total = 0
        for piece_type, value in self.PIECE_VALUES.items():
            total += len(board.pieces(piece_type, color)) * value
        return total

    def _material_text(self, board):
        white_score = self._material_score(board, chess.WHITE)
        black_score = self._material_score(board, chess.BLACK)
        diff = white_score - black_score

        if diff == 0:
            advantage = "Material: equal"
        elif diff > 0:
            advantage = f"Material advantage: White +{diff}"
        else:
            advantage = f"Material advantage: Black +{abs(diff)}"

        return f"{advantage}\nWhite: {white_score} | Black: {black_score}"

    def jump_to_ply(self, ply_index):
        self.review_index = max(0, min(ply_index, len(self.game.board.move_stack)))
        self._render_review_position()

    def previous_move(self):
        if self.review_index > 0:
            self.review_index -= 1
            self._render_review_position()

    def next_move(self):
        if self.review_index < len(self.game.board.move_stack):
            self.review_index += 1
            self._render_review_position()

    def _render_review_position(self):
        board_to_render = self._board_at(self.review_index)
        self.board.interaction_enabled = self.review_index == len(self.game.board.move_stack)
        self.board.render_position(board_to_render.board_fen(), self.game.player_pov)
        self.refresh_sidebar()

    def export_fen(self):
        board_to_export = self._board_at(self.review_index)
        filename, _ = QFileDialog.getSaveFileName(self, "Export FEN", "game_position.fen", "FEN Files (*.fen)")
        if not filename:
            return
        with open(filename, "w", encoding="utf-8") as fen_file:
            fen_file.write(board_to_export.fen())

    def export_pgn(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export PGN", "game.pgn", "PGN Files (*.pgn)")
        if not filename:
            return

        game_node = chess.pgn.Game()
        node = game_node
        for move in self.game.board.move_stack:
            node = node.add_variation(move)

        with open(filename, "w", encoding="utf-8") as pgn_file:
            pgn_file.write(str(game_node))
