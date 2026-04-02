from PySide6.QtCore import QThread, Signal
import chess.engine

class BotWorker(QThread):
    move_ready = Signal(object)
    failed = Signal(object)

    def __init__(self, board, engine_path, time_limit=0.1):
        super().__init__()
        self.board = board.copy()
        self.engine_path = engine_path
        self.time_limit = time_limit

    def run(self):
        engine = None
        try:
            engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            result = engine.play(
                self.board,
                chess.engine.Limit(time=self.time_limit)
            )
            self.move_ready.emit(result.move)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            if engine is not None:
                try:
                    engine.quit()
                except Exception:
                    pass