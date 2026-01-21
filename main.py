import chess.variant

class GameState:
    def __init__(self,variant):
        if variant == "normal":
            self.board = chess.Board()
        elif variant == "antichess":
            self.board = chess.variant.AntichessBoard()
        elif variant == "horde":
            self.board = chess.variant.HordeBoard()
    def legal_moves(self):
        return self.board.legal_moves
    def make_move(self,move):
        self.board.push_san(move)
game=GameState("normal")
game.make_move("e4")
game.make_move("e5")
print(game.legal_moves())