from PySide6.QtGui import QColor,QBrush
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import QApplication
from gui.piece_item import PieceItem
from game.piece import Piece
from gui.board_scene import BoardScene

class ChessBoardWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.square_size = 80
        self.selected_piece = None
        self.scene = BoardScene(self)
        self.setScene(self.scene)

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

    def select_piece(self,piece):
        self.selected_piece = piece

    def move_piece(self,piece,col,row):
        piece.col = col
        piece.row = row

        piece.graphics_item.setPos(
            col * self.square_size,
            abs(piece.row-7) * self.square_size,
        )

    def render_position(self,FEN):
        self.scene.clear()
        self.draw_board()
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        numbers="0123456789"
        col=0
        row=7
        print(FEN)
        for i in FEN:
            if(i in alphabet):
                if(i==i.lower()):
                    color="Black"
                else:
                    color="White"
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
                self.add_piece(
                    Piece(col,row,i),
                    "assets/"+PIECE_MAP[i]+".svg"
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


