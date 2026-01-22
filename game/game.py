import chess

class GameState:
    def __init__(self,chess,variant):
        if variant == "normal":
            self.board = chess.Board()
        elif variant == "antichess":
            self.board = chess.variant.AntichessBoard()
        elif variant == "horde":
            self.board = chess.variant.HordeBoard()
        self.variant = variant
        self.current_player="White"
        self.pieces = []

    def add_piece(self, Piece):
        self.pieces.append(Piece)

    def piece_at(self, col, row):
        return next(
            (p for p in self.pieces if p.col == col and p.row == row),
            None
        )
    def make_move(self,move):
        alphabet={
            0:"a",
            1:"b",
            2:"c",
            3:"d",
            4:"e",
            5:"f",
            6:"g",
            7:"h",
        }
        sanmove=alphabet[int(move[0][0])]+str(int(move[0][1])+1)+alphabet[int(move[1][0])]+str(int(move[1][1])+1)
        self.board.push_san(sanmove)
        for p in self.pieces:
            if(p.col==int(move[0][0]) and p.row==int(move[0][1])):
                for pp in self.pieces:
                    if(pp.col==int(move[1][0]) and pp.row==int(move[1][1])):
                        self.pieces.remove(pp)
                p.col=int(move[1][0])
                p.row=int(move[1][1])
                break

