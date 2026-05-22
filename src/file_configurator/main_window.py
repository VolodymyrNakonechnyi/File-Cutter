"""Main window for batch .txt file operations."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .batch_reduce import BatchReductionResult, reduce_text_files, target_size_to_bytes
from .text_file import TextFileError


TXT_FILE_FILTER = "TXT файли (*.txt)"


class MainWindow(QMainWindow):
    """File-focused utility for reducing supported text files."""

    def __init__(self) -> None:
        super().__init__()
        self._selected_target: Path | None = None

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(self._create_intro_label())
        central_layout.addWidget(self._create_batch_group())
        central_layout.addStretch(1)
        self.setCentralWidget(central_widget)

        self.resize(720, 320)
        self.setWindowTitle("Скорочувач TXT файлів")
        self.statusBar().showMessage("Готово")

    def select_batch_file(self) -> None:
        file_text, _ = QFileDialog.getOpenFileName(
            self,
            "Виберіть TXT файл",
            self._dialog_start_path(),
            TXT_FILE_FILTER,
        )
        if not file_text:
            return

        self._set_selected_target(Path(file_text), "Вибраний файл")

    def select_batch_folder(self) -> None:
        folder_text = QFileDialog.getExistingDirectory(
            self,
            "Виберіть папку з TXT файлами",
            self._dialog_start_path(),
        )
        if not folder_text:
            return

        self._set_selected_target(Path(folder_text), "Вибрана папка")

    def reduce_selected_target(self) -> None:
        if self._selected_target is None:
            self._show_error("Спочатку виберіть файл або папку.")
            return

        target_size = self.target_size_input.value()
        unit = self.unit_input.currentText()
        try:
            target_bytes = target_size_to_bytes(target_size, unit)
        except TextFileError as exc:
            self._show_error(str(exc))
            return

        if not self._confirm_batch_reduction(target_size, unit, target_bytes):
            return

        self._prepare_progress()
        self.reduce_folder_button.setEnabled(False)
        try:
            result = reduce_text_files(
                self._selected_target,
                target_size,
                unit,
                self.fill_smaller_input.isChecked(),
                self._update_progress,
            )
        except TextFileError as exc:
            self._show_error(str(exc))
            return
        finally:
            self.reduce_folder_button.setEnabled(True)

        self._show_batch_results(result)

    def _create_intro_label(self) -> QLabel:
        intro = QLabel(
            "Виберіть TXT файл або папку, задайте потрібний числовий розмір і "
            "скоротіть файли, які більші за цей розмір. Менші файли не змінюються, "
            "якщо окремо не ввімкнути дозаповнення."
        )
        intro.setWordWrap(True)
        intro.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        return intro

    def _create_batch_group(self) -> QGroupBox:
        batch_group = QGroupBox("Скорочення файлів")
        batch_layout = QVBoxLayout(batch_group)

        target_picker_layout = QHBoxLayout()
        self.batch_target_label = QLabel("Файл або папку не вибрано")
        self.batch_target_label.setWordWrap(True)
        self.select_file_button = QPushButton("Вибрати файл...")
        self.select_file_button.clicked.connect(self.select_batch_file)
        self.select_folder_button = QPushButton("Вибрати папку...")
        self.select_folder_button.clicked.connect(self.select_batch_folder)
        target_picker_layout.addWidget(QLabel("Ціль:"))
        target_picker_layout.addWidget(self.batch_target_label, 1)
        target_picker_layout.addWidget(self.select_file_button)
        target_picker_layout.addWidget(self.select_folder_button)

        target_layout = QHBoxLayout()
        self.target_size_input = QSpinBox()
        self.target_size_input.setRange(1, 1_000_000)
        self.target_size_input.setValue(20)
        self.unit_input = QComboBox()
        self.unit_input.addItems(["B", "KB", "MB"])
        self.unit_input.setCurrentText("KB")
        self.unit_input.setEditable(False)
        self.reduce_folder_button = QPushButton("ЗАПУСТИТИ ОБРОБКУ")
        self.reduce_folder_button.setMinimumHeight(48)
        self.reduce_folder_button.setDefault(True)
        self.reduce_folder_button.setStyleSheet(
            """
            QPushButton {
                background-color: #15803d;
                color: white;
                border: 0;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 700;
                padding: 10px 18px;
            }
            QPushButton:hover {
                background-color: #166534;
            }
            QPushButton:pressed {
                background-color: #14532d;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
                color: #e2e8f0;
            }
            """
        )
        self.reduce_folder_button.clicked.connect(self.reduce_selected_target)
        target_layout.addWidget(QLabel("Цільовий розмір:"))
        target_layout.addWidget(self.target_size_input)
        target_layout.addWidget(self.unit_input)
        target_layout.addStretch(1)
        target_layout.addWidget(self.reduce_folder_button)

        self.fill_smaller_input = QCheckBox("Дозаповнити менші файли випадковим текстом до цільового розміру")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Прогрес: 0%")
        self.progress_bar.setTextVisible(True)

        batch_layout.addLayout(target_picker_layout)
        batch_layout.addLayout(target_layout)
        batch_layout.addWidget(self.fill_smaller_input)
        batch_layout.addWidget(self.progress_bar)
        return batch_group

    def _confirm_batch_reduction(self, target_size: int, unit: str, target_bytes: int) -> bool:
        target_label = "файл" if self._selected_target and self._selected_target.is_file() else "папку"
        smaller_behavior = (
            "Файли, які менші за цей розмір, будуть дозаповнені випадковим текстом."
            if self.fill_smaller_input.isChecked()
            else "Файли, які вже менші або рівні цьому розміру, не змінюються."
        )
        result = QMessageBox.question(
            self,
            "Підтвердьте скорочення",
            (
                f"Програма обробить вибрану {target_label} і перезапише TXT файли, "
                f"якщо вони більші за {target_size} {unit} ({target_bytes} байт).\n\n"
                f"{smaller_behavior}\n\n"
                "Цю дію не можна скасувати. Продовжити?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return result == QMessageBox.StandardButton.Yes

    def _dialog_start_path(self) -> str:
        if self._selected_target is None:
            return str(Path.home())
        if self._selected_target.is_file():
            return str(self._selected_target.parent)
        return str(self._selected_target)

    def _set_selected_target(self, path: Path, label: str) -> None:
        self._selected_target = path
        self.batch_target_label.setText(str(path))
        self.statusBar().showMessage(f"{label}: {path}")

    def _prepare_progress(self) -> None:
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Підготовка...")
        self.statusBar().showMessage("Підготовка до обробки файлів...")
        QApplication.processEvents()

    def _update_progress(self, current: int, total: int, path: Path) -> None:
        if total <= 0:
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(1)
            self.progress_bar.setFormat("Файлів для обробки немає")
            return

        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"Оброблено {current}/{total}: {path.name}")
        self.statusBar().showMessage(f"Оброблено {current}/{total}: {path.name}")
        QApplication.processEvents()

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Скорочувач TXT файлів", message)
        self.statusBar().showMessage(message)

    def _show_batch_results(self, result: BatchReductionResult) -> None:
        QMessageBox.information(self, "Обробку завершено", f"Готово.\n\n{result.summary()}")
        self.statusBar().showMessage(
            "Завершено: "
            f"скорочено {len(result.reduced)}, "
            f"дозаповнено {len(result.expanded)}, "
            f"пропущено {len(result.skipped)}, "
            f"помилок {len(result.failed)}"
        )
