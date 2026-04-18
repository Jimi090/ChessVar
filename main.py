import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPalette
from gui.main_window import MainWindow

def apply_dark_theme(app):
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#121212"))
    palette.setColor(QPalette.WindowText, QColor("#e0e0e0"))
    palette.setColor(QPalette.Base, QColor("#1b1b1b"))
    palette.setColor(QPalette.AlternateBase, QColor("#202020"))
    palette.setColor(QPalette.ToolTipBase, QColor("#1e1e1e"))
    palette.setColor(QPalette.ToolTipText, QColor("#f0f0f0"))
    palette.setColor(QPalette.Text, QColor("#e0e0e0"))
    palette.setColor(QPalette.Button, QColor("#1e1e1e"))
    palette.setColor(QPalette.ButtonText, QColor("#f0f0f0"))
    palette.setColor(QPalette.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.Highlight, QColor("#769656"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.Link, QColor("#8fbf72"))
    palette.setColor(QPalette.PlaceholderText, QColor("#7f7f7f"))

    disabled_text = QColor("#6f6f6f")
    palette.setColor(QPalette.Disabled, QPalette.WindowText, disabled_text)
    palette.setColor(QPalette.Disabled, QPalette.Text, disabled_text)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_text)
    palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor("#3d4d30"))
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor("#b0b0b0"))

    app.setPalette(palette)
    app.setStyleSheet(
        "QToolTip { color: #f0f0f0; background-color: #1e1e1e; border: 1px solid #333333; }"
    )

def main():
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
