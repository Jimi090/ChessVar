from PySide6.QtCore import QThread, Signal
import chess.engine

class BotWorker(QThread):
    move_ready = Signal(object)  # chess.Move

    def __init__(self, board, engine_path, time_limit=0.1):
        super().__init__()
        self.board = board.copy()
        self.engine_path = engine_path
        self.time_limit = time_limit

    def run(self):
        engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        result = engine.play(
            self.board,
            chess.engine.Limit(time=self.time_limit)
        )
        engine.quit()
        self.move_ready.emit(result.move)
