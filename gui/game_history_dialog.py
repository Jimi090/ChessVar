from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout

from game.game_history import GameHistoryStore


class GameHistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game History")
        self.resize(620, 520)
        self.setModal(True)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #121212;
                color: #e0e0e0;
            }
            QLabel#Header {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
            }
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #2e2e2e;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
            QListWidget::item {
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                margin: 4px 0;
                padding: 10px;
            }
            QPushButton {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 8px 16px;
                color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            """
        )

        layout = QVBoxLayout(self)
        header = QLabel("Played Games")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.history_list = QListWidget()
        layout.addWidget(self.history_list, stretch=1)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

        self._populate_history()

    def _populate_history(self):
        entries = GameHistoryStore.load()
        self.history_list.clear()

        if not entries:
            self.history_list.addItem(QListWidgetItem("No played games yet."))
            return

        for entry in entries:
            timestamp = entry.get("played_at", "")
            try:
                dt = datetime.fromisoformat(timestamp)
                played_at = dt.strftime("%Y-%m-%d %H:%M UTC")
            except ValueError:
                played_at = timestamp

            result_type = entry.get("result_type", "")
            if result_type == "draw":
                result_line = "Result: Draw"
            else:
                result_line = f"Result: {entry.get('winner', '-') } won"

            text = (
                f"{played_at}\n"
                f"Mode: {entry.get('mode', '-')} | Variant: {entry.get('variant', '-')}\n"
                f"{result_line} ({entry.get('reason', '-')})\n"
                f"Moves: {entry.get('move_count', 0)}"
            )
            self.history_list.addItem(QListWidgetItem(text))
