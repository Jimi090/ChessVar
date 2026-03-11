from PySide6.QtGui import QColor,QBrush,QPen
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QApplication
from PySide6.QtCore import Qt, Signal
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import QGraphicsScene


from gui.game_over_overlay import GameOverOverlay
from gui.piece_item import PieceItem
from game.piece import Piece
from gui.board_scene import BoardScene
from gui.promotion_dialog import PromotionDialog
import chess
import chess.engine
import chess.variant
from game.bot_worker import BotWorker
import random

class ChessBoardWidget(QGraphicsView):
    move_played = Signal()
    def __init__(self,game):
        super().__init__()
        self.game = game
        self.square_size = 80
        self.selected_piece = None
        self.legal_move_markers = []
        self.scene = BoardScene(self)
        self.setScene(self.scene)
        size = self.square_size * 8
        self.scene.setSceneRect(0, 0, size, size)
        self.interaction_enabled = True

    def draw_board(self):
        colors = ["#EEEED2","#769656"]

        for row in range(8):
            for col in range(8):
                color = colors[(row+col) % 2]
                self.scene.addRect(
                    col * self.square_size,
                    row * self.square_size,
                    self.square_size,
                    self.square_size,
                    pen=Qt.NoPen,
                    brush=QBrush(QColor(color)),
                )

    def add_piece(self,piece,svg_path):
        item = PieceItem(piece,svg_path)

        scale=self.square_size/item.boundingRect().width()
        item.setScale(scale)

        item.setPos(
            piece.col * self.square_size,
            abs(piece.row-7) * self.square_size,
        )
        self.scene.addItem(item)
        piece.graphics_item=item

    def is_piece_selectable(self, piece):
        if not self.interaction_enabled or piece is None:
            return False

        is_white_piece = piece.symbol.isupper()
        is_white_turn = self.game.board.turn == chess.WHITE
        return is_white_piece == is_white_turn

    def select_piece(self, piece):
        if not self.is_piece_selectable(piece):
            return False

        self.selected_piece = piece
        self.show_legal_moves(piece)
        return True

    def clear_legal_move_markers(self):
        for marker in self.legal_move_markers:
            self.scene.removeItem(marker)
        self.legal_move_markers.clear()

    def show_legal_moves(self, piece):
        self.clear_legal_move_markers()
        from_col, from_row = piece.col, piece.row

        if self.game.player_pov == "Black":
            from_col = 7 - from_col
            from_row = 7 - from_row

        from_square = chess.square(from_col, from_row)
        normal_marker_size = self.square_size * 0.22
        normal_marker_offset = (self.square_size - normal_marker_size) / 2

        capture_marker_size = self.square_size * 0.66
        capture_marker_offset = (self.square_size - capture_marker_size) / 2

        for move in self.game.board.legal_moves:
            if move.from_square != from_square:
                continue

            target_col = chess.square_file(move.to_square)
            target_row = chess.square_rank(move.to_square)

            if self.game.player_pov == "Black":
                target_col = 7 - target_col
                target_row = 7 - target_row

            is_capture = self.game.board.is_capture(move)
            marker_size = normal_marker_size
            marker_offset = normal_marker_offset
            marker_pen = QPen(QColor(255, 255, 255, 220), 3) if is_capture else QPen(Qt.NoPen)
            marker_brush = QBrush(QColor(235, 70, 70, 150)) if is_capture else QBrush(QColor(35, 95, 35, 170))

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

    def move_piece(self,piece,col,row):
        if not self.interaction_enabled:
            self.clear_legal_move_markers()
            return False
        if not self.is_valid_square(col, row):
            self.clear_legal_move_markers()
            return
        if self.game.player_pov == "White":
            move=[str(piece.col)+str(piece.row),str(col)+str(row)]
        elif self.game.player_pov == "Black":
            move=[str(7-piece.col)+str(7-piece.row),str(col)+str(row)]

        can_be_promoted=False
        new_sym='';
        if piece.symbol.lower()=="p":
            if(piece.symbol.isupper() and row==7) or (piece.symbol.islower() and row==0):
                color = "White" if piece.symbol.isupper() else "Black"
                new_sym = PromotionDialog.get_promotion(color.lower(),self)
                if new_sym:
                    can_be_promoted=True
                    piece.symbol = new_sym.upper() if piece.symbol.isupper() else new_sym.lower()

        if(self.game.is_move_legal(self.game.change_format(move)+new_sym) or\
        (self.game.is_move_legal(self.game.change_format(move)) and not can_be_promoted) ):
            self.game.make_move(move,new_sym)
            self.clear_legal_move_markers()
            if not self.game.vs_bot:
                self.game.player_pov = "White" if self.game.board.turn == chess.WHITE else "Black"
            fen = self.game.board.board_fen()
            self.render_position(fen, self.game.player_pov)
            game_over = self.after_move()
            if self.game.vs_bot and not game_over:
                self.start_bot_move(self.game.bot_level)
            self.move_played.emit()
            return True
        else:
            self.clear_legal_move_markers()
            return False

    def render_position(self,FEN,color="White"):
        self.scene.clear()
        self.clear_legal_move_markers()
        self.draw_board()
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        numbers="0123456789"
        col=0
        row=7
        for i in FEN:
            if(i in alphabet):
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
                if(color=="White"):
                    self.add_piece(
                        Piece(col,row,i),
                        "assets/"+PIECE_MAP[i]+".svg"
                    )
                elif(color=="Black"):
                    self.add_piece(
                        Piece(7-col, 7-row, i),
                        "assets/" + PIECE_MAP[i] + ".svg"
                    )
                col+=1
                if(col==8):
                    col=0
            elif(i in numbers):
                col+=int(i)
                if (col == 8):
                    col = 0
            elif(i=="/"):
                row-=1;
        if self.game.player_pov == "Black" and self.game.is_first_move:
            self.game.is_first_move = False
            if(self.game.vs_bot):
                 self.start_bot_move(self.game.bot_level)

    def on_piece_dropped(self, item, scene_pos):
        size = self.square_size

        col = int(scene_pos.x() // size)
        row = 7 - int(scene_pos.y() // size)

        if self.game.player_pov == "Black":
            col=7-col
            row=7-row
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

        self.overlay = GameOverOverlay(self.viewport(), title, reason)
        self.overlay.setGeometry(self.viewport().rect())
        self.overlay.setAttribute(Qt.WA_DeleteOnClose)
        self.overlay.raise_()
        self.overlay.show()

        self.overlay.new_game_btn.clicked.connect(self.new_game)
        return True

    def new_game(self):
        if self.overlay:
            self.overlay.close()
            self.overlay = None

        self.game.board.reset()
        self.interaction_enabled = True
        if(self.game.player_pov == "White"):
            self.game.player_pov = "Black"
        elif(self.game.player_pov == "Black"):
            self.game.player_pov = "White"
        self.game.is_first_move = True

        self.render_position(self.game.board.board_fen(), self.game.player_pov)

    def start_bot_move(self,level):
        if(level=="Easy"):
            moves = self.game.list_legal_moves()
            moves2=[];
            for i in moves:
                moves2.append(i)
            move = moves2[random.randrange(0, len(moves2))]
            self.on_bot_move(move)
        elif(level=="Medium"):
            engine_path = "engines/fairy-stockfish"

            self.bot_worker = BotWorker(
                self.game.board,
                engine_path,
                time_limit=0.0000000001
            )
            self.bot_worker.move_ready.connect(self.on_bot_move)
            self.bot_worker.start()
        elif (level == "Hard"):
            engine_path = "engines/fairy-stockfish"

            self.bot_worker = BotWorker(
                self.game.board,
                engine_path,
                time_limit=0.5
            )
            self.bot_worker.move_ready.connect(self.on_bot_move)
            self.bot_worker.start()

    def on_bot_move(self, move):
        self.game.apply_bot_move(move)
        fen = self.game.board.board_fen()
        self.render_position(fen, self.game.player_pov)
        self.after_move()
        self.move_played.emit()



