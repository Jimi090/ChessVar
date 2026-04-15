from PySide6.QtGui import QColor, QBrush, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, Signal, QPointF, QTimer
from utils.path_utils import ensure_executable, resource_path
from gui.game_over_overlay import GameOverOverlay
from gui.piece_item import PieceItem
from game.piece import Piece
from gui.board_scene import BoardScene
from gui.promotion_dialog import PromotionDialog
import chess
from game.bot_worker import BotWorker
import random

class ChessBoardWidget(QGraphicsView):
    move_played = Signal()
    interaction_blocked = Signal(str)
    game_finished = Signal(dict)
    BOT_LEVEL_SETTINGS = {
        "Beginner": {"strategy": "random", "think_time": 0.0},
        "Novice": {"strategy": "engine", "think_time": 0.00001},
        "Intermediate": {"strategy": "engine", "think_time": 0.01},
        "Advanced": {"strategy": "engine", "think_time": 0.1},
        "Master": {"strategy": "engine", "think_time": 1.0},
    }

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.square_size = 80
        self.selected_piece = None
        self.legal_move_markers = []
        self.overlay = None
        self.annotation_items = []
        self.highlighted_squares = set()
        self.arrows = set()
        self.preserve_pov_on_move = False

        self.scene = BoardScene(self)
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignCenter)
        self._set_board_pixel_size(self.square_size * 8)
        self.interaction_enabled = True
        self.interaction_block_reason = None
        self._bot_animation_timer = None
        self._history_animation_timer = None
        self._bot_workers = set()
        self._bot_request_id = 0
        self.board_fill_ratio = 0.8
        self.max_board_pixels = 880

    def _set_board_pixel_size(self, pixel_size):
        self.square_size = max(24, pixel_size // 8)
        board_size = self.square_size * 8
        self.scene.setSceneRect(0, 0, board_size, board_size)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        viewport_width = self.viewport().width()
        viewport_height = self.viewport().height()
        if viewport_width <= 0 or viewport_height <= 0:
            return
        target_size = int(viewport_height * self.board_fill_ratio)
        target_size = min(target_size, viewport_width)
        target_size = max(192, target_size)
        target_size = min(target_size, self.max_board_pixels)
        self._set_board_pixel_size(target_size)
        self._render_current_position()

    def draw_board(self):
        colors = ["#EEEED2", "#769656"]

        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                self.scene.addRect(
                    col * self.square_size,
                    row * self.square_size,
                    self.square_size,
                    self.square_size,
                    pen=Qt.NoPen,
                    brush=QBrush(QColor(color)),
                )

    def add_piece(self, piece, svg_path):
        item = PieceItem(piece, svg_path)

        scale = self.square_size / item.boundingRect().width()
        item.setScale(scale)

        item.setPos(
            piece.col * self.square_size,
            abs(piece.row - 7) * self.square_size,
        )
        self.scene.addItem(item)
        piece.graphics_item = item

    def is_piece_selectable(self, piece):
        if not self.interaction_enabled or piece is None:
            return False

        is_white_piece = piece.symbol.isupper()
        is_white_turn = self.game.board.turn == chess.WHITE
        return is_white_piece == is_white_turn

    def select_piece(self, piece):
        if not self.is_piece_selectable(piece):
            if not self.interaction_enabled:
                self.interaction_blocked.emit(self.interaction_block_reason or "busy")
            return False

        self.selected_piece = piece
        self.show_legal_moves(piece)
        return True

    def clear_legal_move_markers(self):
        for marker in self.legal_move_markers:
            self.scene.removeItem(marker)
        self.legal_move_markers.clear()

    def scene_pos_to_board_square(self, scene_pos):
        col = int(scene_pos.x() // self.square_size)
        row = 7 - int(scene_pos.y() // self.square_size)

        if not self.is_valid_square(col, row):
            return None

        if self.game.player_pov == "Black":
            col = 7 - col
            row = 7 - row

        return col, row

    def _board_square_to_scene_top_left(self, col, row):
        scene_col, scene_row = col, row
        if self.game.player_pov == "Black":
            scene_col = 7 - col
            scene_row = 7 - row
        x = scene_col * self.square_size
        y = (7 - scene_row) * self.square_size
        return x, y

    def clear_annotation_items(self):
        for item in self.annotation_items:
            self.scene.removeItem(item)
        self.annotation_items.clear()

    def redraw_annotations(self):
        self.clear_annotation_items()

        for col, row in self.highlighted_squares:
            x, y = self._board_square_to_scene_top_left(col, row)
            highlight_item = self.scene.addRect(
                x,
                y,
                self.square_size,
                self.square_size,
                pen=Qt.NoPen,
                brush=QBrush(QColor(255, 215, 0, 100)),
            )
            highlight_item.setAcceptedMouseButtons(Qt.NoButton)
            highlight_item.setZValue(0.2)
            self.annotation_items.append(highlight_item)

        for start, end in self.arrows:
            self._draw_arrow(start, end)

    def _draw_arrow(self, start, end):
        start_x, start_y = self._board_square_to_scene_top_left(start[0], start[1])
        end_x, end_y = self._board_square_to_scene_top_left(end[0], end[1])

        start_center = QPointF(start_x + self.square_size / 2, start_y + self.square_size / 2)
        end_center = QPointF(end_x + self.square_size / 2, end_y + self.square_size / 2)

        dx = end_center.x() - start_center.x()
        dy = end_center.y() - start_center.y()
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:
            return

        unit_x = dx / length
        unit_y = dy / length
        head_len = min(self.square_size * 0.35, length * 0.4)

        line_end = QPointF(
            end_center.x() - unit_x * head_len,
            end_center.y() - unit_y * head_len,
        )

        line_item = self.scene.addLine(
            start_center.x(),
            start_center.y(),
            line_end.x(),
            line_end.y(),
            QPen(QColor(240, 85, 85, 190), 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin),
        )
        line_item.setAcceptedMouseButtons(Qt.NoButton)
        line_item.setZValue(0.3)
        self.annotation_items.append(line_item)

        perp_x = -unit_y
        perp_y = unit_x
        half_width = self.square_size * 0.14

        left = QPointF(
            line_end.x() + perp_x * half_width,
            line_end.y() + perp_y * half_width,
        )
        right = QPointF(
            line_end.x() - perp_x * half_width,
            line_end.y() - perp_y * half_width,
        )

        arrow_head = QPolygonF([end_center, left, right])
        head_item = self.scene.addPolygon(
            arrow_head,
            pen=QPen(Qt.NoPen),
            brush=QBrush(QColor(240, 85, 85, 220)),
        )
        head_item.setAcceptedMouseButtons(Qt.NoButton)
        head_item.setZValue(0.35)
        self.annotation_items.append(head_item)

    def toggle_square_highlight(self, square):
        if square in self.highlighted_squares:
            self.highlighted_squares.remove(square)
        else:
            self.highlighted_squares.add(square)
        self.redraw_annotations()

    def toggle_arrow(self, start, end):
        arrow = (start, end)
        if arrow in self.arrows:
            self.arrows.remove(arrow)
        else:
            self.arrows.add(arrow)
        self.redraw_annotations()

    def clear_annotations(self):
        self.highlighted_squares.clear()
        self.arrows.clear()
        self.clear_annotation_items()

    def _add_marker(self, target_col, target_row, is_capture):
        normal_marker_size = self.square_size * 0.22
        normal_marker_offset = (self.square_size - normal_marker_size) / 2
        capture_marker_size = self.square_size * 0.66
        capture_marker_offset = (self.square_size - capture_marker_size) / 2

        marker_size = capture_marker_size if is_capture else normal_marker_size
        marker_offset = capture_marker_offset if is_capture else normal_marker_offset
        marker_pen = QPen(QColor(255, 255, 255, 220), 3) if is_capture else QPen(Qt.NoPen)
        marker_brush = QBrush(QColor(235, 70, 70, 150)) if is_capture else QBrush(QColor(35, 95, 35, 170))

        if self.game.player_pov == "Black":
            target_col = 7 - target_col
            target_row = 7 - target_row

        marker = self.scene.addEllipse(
            target_col * self.square_size + marker_offset,
            (7 - target_row) * self.square_size + marker_offset,
            marker_size,
            marker_size,
            pen=marker_pen,
            brush=marker_brush
        )
        marker.setAcceptedMouseButtons(Qt.NoButton)
        marker.setZValue(0.5)
        self.legal_move_markers.append(marker)

    def show_legal_moves(self, piece):
        self.clear_legal_move_markers()
        from_col, from_row = piece.col, piece.row

        if self.game.player_pov == "Black":
            from_col = 7 - from_col
            from_row = 7 - from_row

        from_square = chess.square(from_col, from_row)

        for move in self.game.board.legal_moves:
            if move.from_square != from_square:
                continue

            target_col = chess.square_file(move.to_square)
            target_row = chess.square_rank(move.to_square)
            is_capture = self.game.board.is_capture(move)
            self._add_marker(target_col, target_row, is_capture)

    def _render_current_position(self):
        self.render_position(self.game.get_display_fen(), self.game.player_pov)

    def _finalize_successful_move(self):
        self.clear_legal_move_markers()
        self.clear_annotations()
        self.selected_piece = None
        if not self.game.vs_bot and not self.preserve_pov_on_move:
            self.game.player_pov = "White" if self.game.board.turn == chess.WHITE else "Black"
        self._render_current_position()
        game_over = self.after_move()
        if self.game.vs_bot and not game_over:
            self.start_bot_move(self.game.bot_level)
        self.move_played.emit()
        return True

    def move_piece(self, piece, col, row):
        if not self.interaction_enabled:
            self.clear_legal_move_markers()
            self.interaction_blocked.emit(self.interaction_block_reason or "busy")
            return False
        if not self.is_valid_square(col, row):
            self.clear_legal_move_markers()
            return False
        if self.game.player_pov == "White":
            move = [str(piece.col) + str(piece.row), str(col) + str(row)]
        else:
            move = [str(7 - piece.col) + str(7 - piece.row), str(col) + str(row)]

        can_be_promoted = False
        new_sym = ''
        if piece.symbol.lower() == "p":
            if (piece.symbol.isupper() and row == 7) or (piece.symbol.islower() and row == 0):
                color = "White" if piece.symbol.isupper() else "Black"
                new_sym = PromotionDialog.get_promotion(color.lower(), self)
                if new_sym:
                    can_be_promoted = True
                    piece.symbol = new_sym.upper() if piece.symbol.isupper() else new_sym.lower()

        if (self.game.is_move_legal(self.game.change_format(move) + new_sym) or
                (self.game.is_move_legal(self.game.change_format(move)) and not can_be_promoted)):
            self.game.make_move(move, new_sym)
            return self._finalize_successful_move()

        self.clear_legal_move_markers()
        return False

    def render_position(self, FEN, color="White"):
        self.scene.clear()
        self.clear_legal_move_markers()
        self.annotation_items = []
        self.draw_board()
        self.redraw_annotations()
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        numbers = "0123456789"
        col = 0
        row = 7
        for i in FEN:
            if i in alphabet:
                PIECE_MAP = {
                    "k": "blackKing",
                    "q": "blackQueen",
                    "r": "blackRook",
                    "b": "blackBishop",
                    "n": "blackKnight",
                    "p": "blackPawn",
                    "K": "whiteKing",
                    "Q": "whiteQueen",
                    "R": "whiteRook",
                    "B": "whiteBishop",
                    "N": "whiteKnight",
                    "P": "whitePawn",
                }
                if color == "White":
                    self.add_piece(
                        Piece(col, row, i),
                        resource_path("assets/" + PIECE_MAP[i] + ".svg")
                    )
                elif color == "Black":
                    self.add_piece(
                        Piece(7 - col, 7 - row, i),
                        resource_path("assets/" + PIECE_MAP[i] + ".svg")
                    )
                col += 1
                if col == 8:
                    col = 0
            elif i in numbers:
                col += int(i)
                if col == 8:
                    col = 0
            elif i == "/":
                row -= 1
        if self.game.player_pov == "Black" and self.game.is_first_move:
            self.game.is_first_move = False
            if self.game.vs_bot:
                self.start_bot_move(self.game.bot_level)

    def on_piece_dropped(self, item, scene_pos):
        size = self.square_size

        col = int(scene_pos.x() // size)
        row = 7 - int(scene_pos.y() // size)

        if self.game.player_pov == "Black":
            col = 7 - col
            row = 7 - row
        if not self.move_piece(item.piece, col, row):
            item.setPos(
                item.piece.col * size,
                (7 - item.piece.row) * size
            )
            self.selected_piece = None
            return

        self.selected_piece = None

    def is_valid_square(self, col, row):
        return 0 <= col < 8 and 0 <= row < 8

    def after_move(self):
        result = self.game.get_game_result()
        if not result:
            return False

        if result["type"] == "win":
            title = f"{result['winner']} wins!"
            reason = result["reason"]
        else:
            title = "Draw"
            reason = result["reason"]

        self.game_finished.emit(result)

        self.overlay = GameOverOverlay(self.viewport(), title, reason)
        self.overlay.setGeometry(self.viewport().rect())
        self.overlay.setAttribute(Qt.WA_DeleteOnClose)
        self.overlay.raise_()
        self.overlay.show()

        self.overlay.new_game_btn.clicked.connect(self.new_game)
        self.overlay.close_btn.clicked.connect(self.close_overlay)
        return True

    def close_overlay(self):
        if self.overlay:
            self.overlay.close()
            self.overlay = None

    def new_game(self):
        self.cancel_pending_bot_moves()
        self.close_overlay()

        self.game.reset_board()
        self.interaction_enabled = True
        self.interaction_block_reason = None
        self.clear_annotations()
        if self.game.player_pov == "White":
            self.game.player_pov = "Black"
        elif self.game.player_pov == "Black":
            self.game.player_pov = "White"
        self.game.is_first_move = True

        self.render_position(self.game.get_display_fen(), self.game.player_pov)

    def start_bot_move(self, level):
        self.interaction_enabled = False
        self.interaction_block_reason = "bot"
        level_config = self.BOT_LEVEL_SETTINGS.get(
            level,
            self.BOT_LEVEL_SETTINGS["Intermediate"],
        )
        strategy = level_config["strategy"]
        if strategy == "random":
            moves = list(self.game.list_legal_moves())
            if not moves:
                self.interaction_enabled = True
                self.interaction_block_reason = None
                return
            self._bot_request_id += 1
            request_id = self._bot_request_id
            move = moves[random.randrange(0, len(moves))]
            self.on_bot_move(move)
            return
        engine_path = ensure_executable(resource_path("engines/fairy-stockfish"))
        worker = BotWorker(
            self.game.board,
            engine_path,
            time_limit=level_config["think_time"],
        )
        self._bot_workers.add(worker)

        worker.finished.connect(lambda w=worker: self._cleanup_bot_worker(w))
        worker.move_ready.connect(lambda move, rid=self._bot_request_id: self._on_bot_move_ready(rid, move))
        worker.failed.connect(self._on_bot_worker_failed)
        worker.start()

    def _cleanup_bot_worker(self, worker):
        self._bot_workers.discard(worker)
        worker.deleteLater()

    def _on_bot_move_ready(self, request_id, move):
        if request_id != self._bot_request_id:
            return
        self.on_bot_move(move)

    def _on_bot_worker_failed(self, _message):
        self.interaction_enabled = True
        self.interaction_block_reason = None

    def on_bot_move(self, move):
            if move is None:
                self.interaction_enabled = True
                self.interaction_block_reason = None
                return
            if move not in self.game.board.legal_moves:
                self.interaction_enabled = True
                self.interaction_block_reason = None
                return
            self.interaction_enabled = False
            self.interaction_block_reason = "bot"
            self.animate_bot_move(move)

    def animate_bot_move(self, move):
        moving_piece = self._piece_item_at_square(
            chess.square_file(move.from_square),
            chess.square_rank(move.from_square),
        )
        if moving_piece is None:
            self._finish_bot_move(move)
            return

        target_x, target_y = self._board_square_to_scene_top_left(
            chess.square_file(move.to_square),
            chess.square_rank(move.to_square),
        )
        start_pos = moving_piece.pos()
        steps = 12
        duration_ms = 240
        interval_ms = max(1, duration_ms // steps)
        self._bot_animation_timer = QTimer(self)
        self._bot_animation_timer.setInterval(interval_ms)
        self._bot_animation_step = 0

        def _animate_step():
            self._bot_animation_step += 1
            progress = min(1.0, self._bot_animation_step / steps)
            new_x = start_pos.x() + (target_x - start_pos.x()) * progress
            new_y = start_pos.y() + (target_y - start_pos.y()) * progress
            moving_piece.setPos(new_x, new_y)

            if progress >= 1.0:
                self._bot_animation_timer.stop()
                self._bot_animation_timer.deleteLater()
                self._bot_animation_timer = None
                self._finish_bot_move(move)

        self._bot_animation_timer.timeout.connect(_animate_step)
        self._bot_animation_timer.start()

    def _piece_item_at_square(self, col, row):
        x, y = self._board_square_to_scene_top_left(col, row)
        center = QPointF(x + self.square_size / 2, y + self.square_size / 2)
        item = self.itemAt(self.mapFromScene(center))
        return item if isinstance(item, PieceItem) else None

    def _finish_bot_move(self, move):
        self.game.apply_bot_move(move)
        self.clear_annotations()
        self.interaction_enabled = True
        self.interaction_block_reason = None
        self._render_current_position()
        self.after_move()
        self.move_played.emit()

    def cancel_pending_bot_moves(self):
        self._bot_request_id += 1
        if self._bot_animation_timer:
            self._bot_animation_timer.stop()
            self._bot_animation_timer.deleteLater()
            self._bot_animation_timer = None
        self.interaction_enabled = True
        self.interaction_block_reason = None

    def animate_history_move(self, from_col, from_row, to_col, to_row, on_finished):
        moving_piece = self._piece_item_at_square(from_col, from_row)
        if moving_piece is None:
            on_finished()
            return

        target_x, target_y = self._board_square_to_scene_top_left(to_col, to_row)
        start_pos = moving_piece.pos()
        steps = 6
        duration_ms = 90
        interval_ms = max(1, duration_ms // steps)

        if self._history_animation_timer:
            self._history_animation_timer.stop()
            self._history_animation_timer.deleteLater()

        self._history_animation_timer = QTimer(self)
        self._history_animation_timer.setInterval(interval_ms)
        self._history_animation_step = 0

        def _animate_step():
            self._history_animation_step += 1
            progress = min(1.0, self._history_animation_step / steps)
            new_x = start_pos.x() + (target_x - start_pos.x()) * progress
            new_y = start_pos.y() + (target_y - start_pos.y()) * progress
            moving_piece.setPos(new_x, new_y)

            if progress >= 1.0:
                self._history_animation_timer.stop()
                self._history_animation_timer.deleteLater()
                self._history_animation_timer = None
                on_finished()

        self._history_animation_timer.timeout.connect(_animate_step)
        self._history_animation_timer.start()
