import chess
import chess.variant

class GameState:
    VARIANT_BUILDERS = {
        "standard": chess.Board,
        "normal": chess.Board,
        "suicide": chess.variant.SuicideBoard,
        "giveaway": chess.variant.GiveawayBoard,
        "antichess": chess.variant.AntichessBoard,
        "atomic": chess.variant.AtomicBoard,
        "king of the hill": chess.variant.KingOfTheHillBoard,
        "horde": chess.variant.HordeBoard,
        "three-check": chess.variant.ThreeCheckBoard,
        "crazyhouse": chess.variant.CrazyhouseBoard,
    }
    VARIANT_NAMES = {
        "standard": "Standard",
        "normal": "Standard",
        "suicide": "Suicide",
        "giveaway": "Giveaway",
        "antichess": "Antichess",
        "atomic": "Atomic",
        "king of the hill": "King Of The Hill",
        "horde": "Horde",
        "three-check": "Three-check",
        "crazyhouse": "Crazyhouse",
    }
    TERMINATION_LABELS = {
        "CHECKMATE": "Checkmate",
        "STALEMATE": "Stalemate",
        "INSUFFICIENT_MATERIAL": "Insufficient material",
        "SEVENTYFIVE_MOVES": "Seven-Five move rule",
        "FIVEFOLD_REPETITION": "Fivefold repetition",
        "FIFTY_MOVES": "Fifty-move rule",
        "THREEFOLD_REPETITION": "Threefold repetition",
        "VARIANT_WIN": "Variant win",
        "VARIANT_LOSS": "Variant loss",
        "VARIANT_DRAW": "Variant draw",
    }
    DROP_PIECE_ORDER = {
        chess.PAWN,
        chess.KNIGHT,
        chess.BISHOP,
        chess.ROOK,
        chess.QUEEN,
    }

    def __init__(self,chess_module,variant):
        self.variant = self.normalize_variant_name(variant)
        self.variant_display_name = self.VARIANT_NAMES[self.variant]
        self.board = self._create_board()
        self.player_pov = "White"
        self.pieces = []
        self.is_first_move = True
        self.vs_bot = False
        self.bot_level = "Easy"

    def _create_board(self):
        board_builder = self.VARIANT_BUILDERS.get(self.variant,chess.Board)
        return board_builder()

    def reset_board(self):
        self.board = self._create_board()

    def normalize_variant_name(self, variant):
        normalized =str(variant.strip().lower().replace("_"," ").replace("-","-"))
        aliases = {
            "": "standard",
            "standard": "standard",
            "normal": "standard",
            "suicide": "suicide",
            "giveaway": "giveaway",
            "antichess": "antichess",
            "atomic": "atomic",
            "king of the hill": "king of the hill",
            "kingofthehill": "king of the hill",
            "koth": "king of the hill",
            "horde": "horde",
            "three-check": "three-check",
            "three check": "three-check",
            "threecheck": "three-check",
            "crazyhouse": "crazyhouse",
        }
        return aliases.get(normalized, "standard")

    def add_piece(self, Piece):
        self.pieces.append(Piece)

    def list_legal_moves(self):
        return self.board.legal_moves

    def is_move_legal(self, move):
        legal_moves = self.board.legal_moves
        if(move[:2] == move[2:]):
            return False
        return chess.Move.from_uci(move) in legal_moves

    def change_format(self, move):
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

    def make_move(self, move, pawn_promotion_symbol=''):
        if move[0] == move[1]:
            return False
        uci_move = self.change_format(move) + pawn_promotion_symbol
        if self.is_move_legal(uci_move):
            self.board.push(chess.Move.from_uci(uci_move))
            self.print_game_state()
            return True
        return False

    def _build_drop_move(self, piece_type, col, row):
        return chess.Move(to_square=chess.square(col, row), drop=piece_type)

    def supports_drops(self):
        return self.variant == "crazyhouse" and hasattr(self.board, "pockets")

    def is_drop_legal(self, piece_type, col, row):
        if not self.supports_drops():
            return False
        move = self._build_drop_move(piece_type, col, row)
        return move in self.board.legal_moves

    def make_drop_move(self, piece_type, col, row):
        if not self.is_drop_legal(piece_type, col, row):
            return False
        self.board.push(self._build_drop_move(piece_type, col, row))
        self.print_game_state()
        return True

    def get_pocket_counts(self, color, board=None):
        if not self.supports_drops():
            return {}
        board = board or self.board
        pocket = board.pockets[color]
        return {
            piece_type: pocket.count(piece_type)
            for piece_type in self.DROP_PIECE_ORDER
        }

    def get_display_fen(self, board=None):
        board = board or self.board
        board_fen = board.board_fen()
        if "[" in board_fen:
            board_fen = board_fen.split("[", 1)[0]
        return board_fen.replace("~", "")

    def print_game_state(self):
        print(self.board)

    def is_checkmate(self):
        return self.board.is_checkmate()

    def _variant_reason(self, outcome):
        if outcome.termination.name not in {"VARIANT_WIN", "VARIANT_LOSS", "VARIANT_DRAW"}:
            return None

        variant_reasons = {
            "suicide": {
                "VARIANT_WIN": "All pieces lost or no legal moves available",
                "VARIANT_LOSS": "Opponent lost all pieces or has no legal moves",
                "VARIANT_DRAW": "Variant draw",
            },
            "giveaway": {
                "VARIANT_WIN": "All pieces given away or no legal moves available",
                "VARIANT_LOSS": "Opponent gave away all pieces or has no legal moves",
                "VARIANT_DRAW": "Variant draw",
            },
            "antichess": {
                "VARIANT_WIN": "All pieces lost or no legal moves available",
                "VARIANT_LOSS": "Opponent lost all pieces or has no legal moves",
                "VARIANT_DRAW": "Variant draw",
            },
            "atomic": {
                "VARIANT_WIN": "Atomic king explosion",
                "VARIANT_LOSS": "Atomic king explosion",
                "VARIANT_DRAW": "Variant draw",
            },
            "king of the hill": {
                "VARIANT_WIN": "King reached the center",
                "VARIANT_LOSS": "King reached the center",
                "VARIANT_DRAW": "Variant draw",
            },
            "horde": {
                "VARIANT_WIN": "The horde was eliminated",
                "VARIANT_LOSS": "The horde was eliminated",
                "VARIANT_DRAW": "Variant draw",
            },
            "three-check": {
                "VARIANT_WIN": "Three checks delivered",
                "VARIANT_LOSS": "Three checks delivered",
                "VARIANT_DRAW": "Variant draw",
            },
            "crazyhouse": {
                "VARIANT_WIN": "Variant win",
                "VARIANT_LOSS": "Variant loss",
                "VARIANT_DRAW": "Variant draw",
            },
        }

        return variant_reasons.get(self.variant, {}).get(outcome.termination.name)

    def get_game_result(self):
        outcome = self.board.outcome(claim_draw=True)
        if not outcome:
            return None
        reason = self._variant_reason(outcome)
        if not reason:
            reason = self.TERMINATION_LABELS.get(
                outcome.termination.name,
                outcome.termination.name.replace("_", " ").title(),
            )
        if outcome.winner is None:
            return {
                "type":"draw",
                "reason": reason,
            }

        winner = "White" if outcome.winner == chess.WHITE else "Black"
        return {
            "type":"win",
            "winner": winner,
            "reason": reason,
        }

    def apply_bot_move(self, move):
        if move is None:
            return
        self.board.push(move)

