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
        self.player_pov= "White"
        self.pieces = []
        self.is_first_move = True

    def add_piece(self, Piece):
        self.pieces.append(Piece)

    def list_legal_moves(self):
        return self.board.legal_moves

    def is_move_legal(self,move):
        legal_moves = self.board.legal_moves
        if(move[:2]==move[2:]):
            return False
        if(chess.Move.from_uci(move) in legal_moves):
            return True
        else:
            return False

    def change_format(self,move):
        #from [41,43] to "e2e4"
        alphabet = {
            0: "a",
            1: "b",
            2: "c",
            3: "d",
            4: "e",
            5: "f",
            6: "g",
            7: "h",
        }
        sanmove = alphabet[int(move[0][0])] + str(int(move[0][1]) + 1) + alphabet[int(move[1][0])] + str(
            int(move[1][1]) + 1)
        return sanmove

    def make_move(self,move,pawn_promotion_symbol=''):
        if move[0]==move[1]:
            return False
        sanmove = self.change_format(move)
        if self.is_move_legal(sanmove+pawn_promotion_symbol):
            self.board.push_san(self.change_format(move)+pawn_promotion_symbol)
            self.print_game_state()
            return True
        else:
            return False

    def print_game_state(self):
        print(self.board)

    def is_checkmate(self):
        return self.board.is_checkmate()

    def get_game_result(self):
        board = self.board

        if board.is_checkmate():
            winner = "White" if board.turn == chess.BLACK else "Black"
            return {
                "type": "win",
                "winner": winner,
                "reason": "Checkmate"
            }
        if board.is_stalemate():
            return {
                "type": "draw",
                "reason": "Stalemate"
            }
        if board.is_insufficient_material():
            return {
                "type": "draw",
                "reason": "Isufficient material"
            }
        if board.can_claim_threefold_repetition():
            return {
                "type": "draw",
                "reason": "Threefold repetition"
            }
        if board.can_claim_fifty_moves():
            return {
                "type": "draw",
                "reason": "Fifty moves rule"
            }
        return None

    def apply_bot_move(self, move):
        if move == None:
            return
        self.board.push(move)

