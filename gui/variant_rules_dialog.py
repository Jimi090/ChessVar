from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class VariantRulesDialog(QDialog):
    def __init__(self, variant_name, rules_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{variant_name} Rules")
        self.setModal(True)
        self.setMinimumWidth(460)

        self.setStyleSheet("""
            QDialog {
                background-color: #1b1b1b;
                color: #e0e0e0;
                font-family: Arial;
            }
            QLabel#Title {
                font-size: 22px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#Rules {
                background-color: #121212;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 16px;
                line-height: 1.4em;
            }
            QPushButton {
                background-color: #769656;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                color: white;
                padding: 10px 18px;
            }
            QPushButton:hover {
                background-color: #8fbf72;
            }
            QPushButton:pressed {
                background-color: #5c7f45;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel(f"{variant_name} Rules")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)

        rules_label = QLabel(rules_text)
        rules_label.setObjectName("Rules")
        rules_label.setWordWrap(True)
        rules_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(rules_label)
        layout.addWidget(close_button, alignment=Qt.AlignRight)
