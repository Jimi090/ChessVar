from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton
from PySide6.QtSvgWidgets import QSvgWidget
from utils.path_utils import resource_path


class PromotionDialog(QDialog):
    def __init__(self,color,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pawn Promotion")
        self.selected_symbol = None

        layout = QHBoxLayout(self)

        PIECE_MAP = {
            'q': resource_path(f"assets/{color}Queen.svg"),
            'r': resource_path(f"assets/{color}Rook.svg"),
            'b': resource_path(f"assets/{color}Bishop.svg"),
            'n': resource_path(f"assets/{color}Knight.svg")

        }

        for sym,path in PIECE_MAP.items():
            btn = QPushButton()
            btn.setFixedSize(70,70)

            svg = QSvgWidget(path,btn)
            svg.setFixedSize(64,64)

            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(3, 3, 3, 3)
            btn_layout.addWidget(svg)

            btn.clicked.connect(lambda checked, s=sym: self.choose(s))
            layout.addWidget(btn)
        self.setLayout(layout)
    def choose(self,symbol):
        self.selected_symbol = symbol
        self.accept()
    @staticmethod
    def get_promotion(color,parent=None):
        dialog = PromotionDialog(color,parent)
        dialog.exec_()
        return dialog.selected_symbol
