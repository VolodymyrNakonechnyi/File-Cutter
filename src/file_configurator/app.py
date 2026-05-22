"""Application bootstrap for File Configurator."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow


def main() -> int:
    """Start the Qt application."""

    app = QApplication(sys.argv)
    app.setApplicationName("Скорочувач TXT файлів")
    window = MainWindow()
    window.show()
    return app.exec()
