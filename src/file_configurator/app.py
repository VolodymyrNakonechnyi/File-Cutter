"""Application bootstrap for File Configurator."""

import sys

try:
    from PySide6.QtWidgets import QApplication
except ImportError:  # pragma: no cover - exercised only on Python 3.6/PySide2 installs.
    from PySide2.QtWidgets import QApplication

from .main_window import MainWindow


def main() -> int:
    """Start the Qt application."""

    app = QApplication(sys.argv)
    app.setApplicationName("Генератор згенерованого тексту з TXT")
    window = MainWindow()
    window.show()
    return app.exec()
