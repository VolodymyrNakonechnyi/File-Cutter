"""Main window for splitting TXT sources into generated text files."""

from pathlib import Path
from typing import List, Optional

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QFileDialog,
        QDoubleSpinBox,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover - exercised only on Python 3.6/PySide2 installs.
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import (
        QApplication,
        QFileDialog,
        QDoubleSpinBox,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

from .generated_text_splitter import (
    DistributionSettings,
    GenerationResult,
    build_size_distribution_report,
    collect_txt_sources,
    estimate_output_count,
    total_input_size,
    write_generated_text_chunks,
)
from .text_file import TextFileError


TXT_FILE_FILTER = "TXT файли (*.txt)"

try:
    ALIGN_LEFT = Qt.AlignmentFlag.AlignLeft
    ALIGN_TOP = Qt.AlignmentFlag.AlignTop
except AttributeError:  # PySide2
    ALIGN_LEFT = Qt.AlignLeft
    ALIGN_TOP = Qt.AlignTop

try:
    MESSAGE_YES = QMessageBox.StandardButton.Yes
    MESSAGE_NO = QMessageBox.StandardButton.No
except AttributeError:  # PySide2
    MESSAGE_YES = QMessageBox.Yes
    MESSAGE_NO = QMessageBox.No


class MainWindow(QMainWindow):
    """Ukrainian UI for slicing TXT input into generated text output files."""

    def __init__(self) -> None:
        super().__init__()
        self._sources = []  # type: List[Path]
        self._destination = None  # type: Optional[Path]

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(self._create_intro_label())
        central_layout.addWidget(self._create_source_group())
        central_layout.addWidget(self._create_destination_group())
        central_layout.addWidget(self._create_distribution_group())
        central_layout.addWidget(self._create_generation_group())
        central_layout.addStretch(1)
        self.setCentralWidget(central_widget)

        self.resize(860, 520)
        self.setWindowTitle("Генератор згенерованого тексту з TXT")
        self.statusBar().showMessage("Готово")
        self._update_preview()

    def select_source_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Виберіть TXT файли",
            str(Path.home()),
            TXT_FILE_FILTER,
        )
        if not paths:
            return
        self._set_sources(collect_txt_sources(paths))

    def select_source_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Виберіть папку з TXT файлами", str(Path.home()))
        if not folder:
            return
        try:
            self._set_sources(collect_txt_sources(folder=folder))
        except TextFileError as exc:
            self._show_error(str(exc))

    def select_destination_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Виберіть кінцеву папку", str(Path.home()))
        if not folder:
            return
        self._destination = Path(folder)
        self.destination_label.setText(str(self._destination))
        self.statusBar().showMessage(f"Кінцева папка: {self._destination}")
        self._update_preview()

    def generate_text(self) -> None:
        if not self._sources:
            self._show_error("Спочатку виберіть TXT файли або папку з TXT файлами.")
            return
        if self._destination is None:
            self._show_error("Спочатку виберіть кінцеву папку.")
            return

        try:
            settings = self._distribution_settings()
            settings.validate()
        except TextFileError as exc:
            self._show_error(str(exc))
            return

        if not self._confirm_generation():
            return

        self._prepare_progress()
        self.generate_button.setEnabled(False)
        try:
            result = write_generated_text_chunks(self._sources, self._destination, settings, self._update_progress)
        except TextFileError as exc:
            self._show_error(str(exc))
            return
        finally:
            self.generate_button.setEnabled(True)

        distribution_text = self._build_distribution_text(result)
        self._show_generation_results(result, distribution_text)

    def _create_intro_label(self) -> QLabel:
        intro = QLabel(
            "Завантажте TXT файли або папку, налаштуйте нормальний розподіл розмірів "
            "і у кінцеву папку буде згенеровано багато generated_text_XXXXXX.txt файлів. "
            "Джерельні файли не змінюються."
        )
        intro.setWordWrap(True)
        intro.setAlignment(ALIGN_LEFT | ALIGN_TOP)
        return intro

    def _create_source_group(self) -> QGroupBox:
        group = QGroupBox("Джерело")
        layout = QVBoxLayout(group)
        button_layout = QHBoxLayout()
        self.source_label = QLabel("TXT джерела не вибрані")
        self.source_label.setWordWrap(True)
        self.select_files_button = QPushButton("Вибрати TXT файли...")
        self.select_files_button.clicked.connect(self.select_source_files)
        self.select_folder_button = QPushButton("Вибрати папку...")
        self.select_folder_button.clicked.connect(self.select_source_folder)
        button_layout.addWidget(self.select_files_button)
        button_layout.addWidget(self.select_folder_button)
        button_layout.addStretch(1)
        layout.addLayout(button_layout)
        layout.addWidget(self.source_label)
        return group

    def _create_destination_group(self) -> QGroupBox:
        group = QGroupBox("Кінцева папка")
        layout = QHBoxLayout(group)
        self.destination_label = QLabel("Кінцеву папку не вибрано")
        self.destination_label.setWordWrap(True)
        self.select_destination_button = QPushButton("Вибрати кінцеву папку...")
        self.select_destination_button.clicked.connect(self.select_destination_folder)
        layout.addWidget(self.destination_label, 1)
        layout.addWidget(self.select_destination_button)
        return group

    def _create_distribution_group(self) -> QGroupBox:
        group = QGroupBox("Нормальний розподіл розмірів")
        layout = QHBoxLayout(group)
        self.mean_kb_input = self._size_spinbox(2.5, minimum=0.01)
        self.std_kb_input = self._size_spinbox(1.0, minimum=0.01)
        for label, widget in (
            ("Середнє KB:", self.mean_kb_input),
            ("Середньо-квадратичне відхилення KB:", self.std_kb_input),
        ):
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)
        layout.addStretch(1)
        return group

    def _create_generation_group(self) -> QGroupBox:
        group = QGroupBox("Генерація")
        layout = QVBoxLayout(group)
        self.preview_label = QLabel("Попередній розрахунок недоступний")
        self.preview_label.setWordWrap(True)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Прогрес: 0%")
        self.generate_button = QPushButton("Згенерувати текстові файли")
        self.generate_button.setMinimumHeight(52)
        self.generate_button.setDefault(True)
        self.generate_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7c3aed;
                color: white;
                border: 0;
                border-radius: 8px;
                font-size: 17px;
                font-weight: 700;
                padding: 12px 20px;
            }
            QPushButton:hover { background-color: #6d28d9; }
            QPushButton:pressed { background-color: #5b21b6; }
            QPushButton:disabled { background-color: #94a3b8; color: #e2e8f0; }
            """
        )
        self.generate_button.clicked.connect(self.generate_text)
        layout.addWidget(self.preview_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.generate_button)
        return group

    def _size_spinbox(self, value: float, minimum: float = 0.0) -> QDoubleSpinBox:
        widget = QDoubleSpinBox()
        widget.setRange(minimum, 1_000_000.0)
        widget.setDecimals(2)
        widget.setSingleStep(0.1)
        widget.setValue(value)
        widget.valueChanged.connect(self._update_preview)
        return widget

    def _distribution_settings(self) -> DistributionSettings:
        return DistributionSettings(
            mean_kb=self.mean_kb_input.value(),
            std_kb=self.std_kb_input.value(),
        )

    def _set_sources(self, sources: List[Path]) -> None:
        self._sources = sources
        if not sources:
            self.source_label.setText("У виборі немає TXT файлів")
        else:
            self.source_label.setText(f"Вибрано TXT файлів: {len(sources)}")
        self._update_preview()

    def _update_preview(self) -> None:
        if not hasattr(self, "preview_label"):
            return
        if not self._sources:
            self.preview_label.setText("Виберіть TXT джерела для попереднього розрахунку.")
            return
        try:
            settings = self._distribution_settings()
            settings.validate()
            total_bytes = total_input_size(self._sources)
            estimate = estimate_output_count(total_bytes, settings)
        except (OSError, TextFileError) as exc:
            self.preview_label.setText(f"Попередній розрахунок недоступний: {exc}")
            return

        self.preview_label.setText(
            f"Вхідний обсяг: {total_bytes:,} байт. "
            f"Очікувано файлів: приблизно {estimate:,}. "
            f"Destination: {self._destination or 'не вибрано'}"
        )

    def _confirm_generation(self) -> bool:
        existing = list(self._destination.glob("generated_text_*.txt")) if self._destination else []
        warning = ""
        if existing:
            warning = (
                f"\n\nУ кінцевій папці вже є {len(existing)} generated_text_*.txt файлів. "
                "Вони можуть бути перезаписані."
            )
        result = QMessageBox.question(
            self,
            "Підтвердьте генерацію",
            f"Буде згенеровано generated_text_XXXXXX.txt файли у вибрану кінцеву папку. Продовжити?{warning}",
            MESSAGE_YES | MESSAGE_NO,
            MESSAGE_NO,
        )
        return result == MESSAGE_YES

    def _prepare_progress(self) -> None:
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Підготовка...")
        self.statusBar().showMessage("Підготовка до генерації...")
        QApplication.processEvents()

    def _update_progress(self, file_count: int, output_bytes: int, total_bytes: int, output_path: Path) -> None:
        value = 1000 if total_bytes <= 0 else min(1000, round((output_bytes / total_bytes) * 1000))
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"Створено {file_count} файлів: {output_path.name}")
        self.statusBar().showMessage(f"Створено {file_count} файлів")
        QApplication.processEvents()

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Генератор згенерованого тексту з TXT", message)
        self.statusBar().showMessage(message)

    def _build_distribution_text(self, result: GenerationResult) -> str:
        if not result.generated_paths:
            return "\n\nДіаграму не створено: немає файлів згенерованого тексту."
        self.progress_bar.setFormat("Будую діаграму...")
        self.statusBar().showMessage("Будую діаграму розподілу розмірів...")
        QApplication.processEvents()
        try:
            report = build_size_distribution_report(
                result.generated_paths,
                result.destination / "generated_text_sizes_histogram.svg",
            )
        except (OSError, TextFileError) as exc:
            return f"\n\nДіаграму не створено: {exc}"
        return f"\n\n{report.to_text()}"

    def _show_generation_results(self, result: GenerationResult, distribution_text: str) -> None:
        self.progress_bar.setValue(1000)
        self.progress_bar.setFormat("Готово")
        QMessageBox.information(
            self,
            "Генерацію завершено",
            (
                f"Створено файлів: {result.generated_files}\n"
                f"Вихідний обсяг: {result.output_bytes:,} байт\n"
                f"Кінцева папка: {result.destination}"
                f"{distribution_text}"
            ),
        )
        self.statusBar().showMessage(f"Готово: створено {result.generated_files} файлів")
