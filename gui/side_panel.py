from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox
)
class SidePanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Variant"))
        layout.addWidget(QComboBox())

        layout.addWidget(QLabel("Mode"))
        layout.addWidget(QComboBox())

        layout.addWidget(QLabel("New Game"))
        layout.addStretch()
