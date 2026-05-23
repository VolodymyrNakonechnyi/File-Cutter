"""Batch reduction services for supported text files."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union

from .text_file import TextFileError
from .tiny_text_model import generate_language_like_padding


BYTES_PER_KB = 1024
BYTES_PER_MB = BYTES_PER_KB * 1024
SIZE_UNIT_FACTORS = {
    "B": 1,
    "KB": BYTES_PER_KB,
    "MB": BYTES_PER_MB,
}
ProgressCallback = Callable[[int, int, Path], None]


@dataclass(frozen=True)
class BatchFileResult:
    """Outcome for one file or skipped folder entry."""

    path: Path
    reason: str
    original_size: Optional[int] = None
    final_size: Optional[int] = None


@dataclass
class BatchReductionResult:
    """Aggregated outcome for a folder reduction run."""

    reduced: List[BatchFileResult] = field(default_factory=list)
    expanded: List[BatchFileResult] = field(default_factory=list)
    skipped: List[BatchFileResult] = field(default_factory=list)
    failed: List[BatchFileResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.reduced) + len(self.expanded) + len(self.skipped) + len(self.failed)

    def summary(self) -> str:
        return (
            f"Скорочено: {len(self.reduced)}\n"
            f"Дозаповнено: {len(self.expanded)}\n"
            f"Пропущено: {len(self.skipped)}\n"
            f"Помилки: {len(self.failed)}"
        )

    def detailed_lines(self) -> List[str]:
        lines = []  # type: List[str]
        for label, items in (
            ("Скорочено", self.reduced),
            ("Дозаповнено", self.expanded),
            ("Пропущено", self.skipped),
            ("Помилки", self.failed),
        ):
            if not items:
                continue
            lines.append(f"{label}:")
            lines.extend(f"- {item.path.name}: {item.reason}" for item in items)
        return lines

    def message(self) -> str:
        details = "\n".join(self.detailed_lines())
        if not details:
            return self.summary()
        return f"{self.summary()}\n\n{details}"


def target_size_to_bytes(value: Union[int, str], unit: str) -> int:
    """Validate a positive integer size value and return bytes."""

    if unit not in SIZE_UNIT_FACTORS:
        raise TextFileError("Виберіть підтримувану одиницю розміру: B, KB або MB.")

    if isinstance(value, bool):
        raise TextFileError("Цільовий розмір має бути додатним цілим числом.")

    if isinstance(value, int):
        target_size = value
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped.isdigit():
            raise TextFileError("Цільовий розмір має бути додатним цілим числом.")
        target_size = int(stripped)
    else:
        raise TextFileError("Цільовий розмір має бути додатним цілим числом.")

    if target_size <= 0:
        raise TextFileError("Цільовий розмір має бути додатним цілим числом.")

    return target_size * SIZE_UNIT_FACTORS[unit]


def target_size_kb_to_bytes(value: Union[int, str]) -> int:
    """Validate a positive integer KB value and return bytes."""

    return target_size_to_bytes(value, "KB")


def scan_batch_folder(folder: Union[str, Path]) -> Tuple[List[Path], List[BatchFileResult]]:
    """Return top-level .txt files and skipped unsupported entries."""

    folder_path = Path(folder)
    if not folder_path.exists():
        raise TextFileError(f"Папку не знайдено: {folder_path}")
    if not folder_path.is_dir():
        raise TextFileError(f"Вибраний шлях не є папкою: {folder_path}")

    txt_files = []  # type: List[Path]
    skipped = []  # type: List[BatchFileResult]

    try:
        entries = sorted(folder_path.iterdir(), key=lambda path: path.name.lower())
    except OSError as exc:
        raise TextFileError(f"Не вдалося просканувати папку {folder_path}: {exc}") from exc

    for entry in entries:
        if entry.is_dir():
            skipped.append(BatchFileResult(entry, "Підпапку пропущено."))
        elif entry.suffix.lower() == ".txt":
            txt_files.append(entry)
        else:
            skipped.append(BatchFileResult(entry, "Непідтримуваний тип файлу пропущено."))

    return txt_files, skipped


def scan_batch_target(target: Union[str, Path]) -> Tuple[List[Path], List[BatchFileResult]]:
    """Return supported .txt files for either one file or a top-level folder scan."""

    target_path = Path(target)
    if not target_path.exists():
        raise TextFileError(f"Шлях не знайдено: {target_path}")

    if target_path.is_dir():
        return scan_batch_folder(target_path)

    if target_path.suffix.lower() == ".txt":
        return [target_path], []

    return [], [BatchFileResult(target_path, "Непідтримуваний тип файлу пропущено.")]


def truncate_utf8_to_bytes(content: str, max_bytes: int) -> str:
    """Truncate text to a UTF-8 byte limit without splitting characters."""

    if max_bytes < 0:
        raise TextFileError("Цільовий розмір у байтах не може бути від'ємним.")

    encoded = content.encode("utf-8")
    if len(encoded) <= max_bytes:
        return content

    return encoded[:max_bytes].decode("utf-8", errors="ignore")


def truncate_utf8_bytes(data: bytes, max_bytes: int) -> bytes:
    """Truncate UTF-8 bytes and return valid UTF-8 bytes."""

    if len(data) <= max_bytes:
        return data
    return data[:max_bytes].decode("utf-8", errors="ignore").encode("utf-8")


def generate_random_utf8_padding(size_bytes: int) -> bytes:
    """Generate random language-like text bytes, which are valid UTF-8."""

    if size_bytes <= 0:
        return b""

    return generate_language_like_padding(size_bytes)


def expand_utf8_bytes(data: bytes, target_bytes: int) -> bytes:
    """Append random UTF-8 text until data reaches the target byte size."""

    data.decode("utf-8")
    if len(data) >= target_bytes:
        return data
    return data + generate_random_utf8_padding(target_bytes - len(data))


def reduce_text_files(
    target: Union[str, Path],
    target_size: Union[int, str],
    unit: str = "KB",
    fill_smaller: bool = False,
    progress_callback: Optional[ProgressCallback] = None,
) -> BatchReductionResult:
    """Reduce one .txt file or top-level .txt files in a folder to the target size."""

    target_bytes = target_size_to_bytes(target_size, unit)
    txt_files, skipped = scan_batch_target(target)
    result = BatchReductionResult(skipped=skipped)

    total_files = len(txt_files)
    for index, path in enumerate(txt_files, start=1):
        try:
            original_data = path.read_bytes()
            original_size = len(original_data)
            if original_size < target_bytes and fill_smaller:
                expanded_data = expand_utf8_bytes(original_data, target_bytes)
                path.write_bytes(expanded_data)
                result.expanded.append(
                    BatchFileResult(
                        path,
                        f"Дозаповнено з {original_size} байт до {len(expanded_data)} байт.",
                        original_size,
                        len(expanded_data),
                    )
                )
                continue

            if original_size <= target_bytes:
                result.skipped.append(
                    BatchFileResult(
                        path,
                        "Файл уже не перевищує цільовий розмір.",
                        original_size,
                        original_size,
                    )
                )
                continue

            original_data.decode("utf-8")
            reduced_data = truncate_utf8_bytes(original_data, target_bytes)
            path.write_bytes(reduced_data)
            result.reduced.append(
                BatchFileResult(
                    path,
                    f"Скорочено з {original_size} байт до {len(reduced_data)} байт.",
                    original_size,
                    len(reduced_data),
                )
            )
        except UnicodeDecodeError as exc:
            result.failed.append(BatchFileResult(path, "Не вдалося прочитати як UTF-8 текст."))
        except OSError as exc:
            result.failed.append(BatchFileResult(path, f"Помилка файлової операції: {exc}"))
        finally:
            if progress_callback is not None:
                progress_callback(index, total_files, path)

    return result


def reduce_folder_text_files(folder: Union[str, Path], target_size_kb: Union[int, str]) -> BatchReductionResult:
    """Reduce oversized top-level .txt files in a folder to the target KB size."""

    return reduce_text_files(folder, target_size_kb, "KB")
