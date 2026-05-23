"""Services for splitting TXT sources into generated text output files."""

import codecs
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from statistics import mean, median
from typing import Callable, Iterable, List, Optional, Set, Tuple, Union
from xml.sax.saxutils import escape

from scipy.stats import norm

from .text_file import TextFileError


BYTES_PER_KB = 1024
DEFAULT_READ_SIZE = 64 * 1024
OUTPUT_FILE_PREFIX = "generated_text"
ProgressCallback = Callable[[int, int, int, Path], None]


@dataclass(frozen=True)
class DistributionSettings:
    mean_kb: float = 2.5
    std_kb: float = 1.0

    def validate(self) -> None:
        if self.mean_kb <= 0:
            raise TextFileError("Середнє значення має бути більшим за нуль.")
        if self.std_kb <= 0:
            raise TextFileError("Стандартне відхилення має бути більшим за нуль.")

    @property
    def mean_bytes(self) -> int:
        return max(1, round(self.mean_kb * BYTES_PER_KB))


@dataclass(frozen=True)
class GenerationResult:
    generated_files: int
    output_bytes: int
    destination: Path
    generated_paths: Tuple[Path, ...]


@dataclass(frozen=True)
class HistogramBucket:
    lower: int
    upper: int
    count: int


@dataclass(frozen=True)
class SizeDistributionReport:
    histogram_path: Path
    file_count: int
    min_bytes: int
    median_bytes: float
    mean_bytes: float
    max_bytes: int
    buckets: Tuple[HistogramBucket, ...]

    def to_text(self) -> str:
        lines = [
            "Згенеровано діаграму розподілу розмірів файлів згенерованого тексту у файлі:",
            str(self.histogram_path),
            "Коротка зводка:",
            f"- Файлів: {self.file_count}",
            f"- Мінімум: {self.min_bytes} B",
            f"- Медіана: {_format_number(self.median_bytes)} B",
            f"- Середнє: {self.mean_bytes:.1f} B",
            f"- Максимум: {self.max_bytes} B",
            "Текстовий вигляд розподілу:",
        ]
        max_count = max((bucket.count for bucket in self.buckets), default=0)
        for bucket in self.buckets:
            bar_width = 0 if max_count == 0 else round((bucket.count / max_count) * 24)
            bar = "█" * max(1, bar_width) if bucket.count else ""
            lines.append(f"{bucket.lower:>5}-{bucket.upper:<5} {bucket.count:>4} {bar}")
        return "\n".join(lines)


def sample_chunk_size_bytes(settings: DistributionSettings, random_state: Optional[object] = None) -> int:
    """Sample one positive target chunk size using SciPy normal distribution."""

    settings.validate()
    distribution = norm(loc=settings.mean_kb, scale=settings.std_kb)
    while True:
        sample_kb = float(distribution.rvs(random_state=random_state))
        random_state = None
        if sample_kb > 0:
            return max(1, round(sample_kb * BYTES_PER_KB))


def collect_txt_sources(
    paths: Iterable[Union[str, Path]] = (),
    folder: Optional[Union[str, Path]] = None,
) -> List[Path]:
    """Collect selected TXT files and top-level TXT files from an optional folder."""

    sources = []  # type: List[Path]
    seen = set()  # type: Set[Path]

    for path_value in paths:
        path = Path(path_value)
        if path.is_file() and path.suffix.lower() == ".txt":
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                sources.append(path)

    if folder is not None:
        folder_path = Path(folder)
        if not folder_path.exists():
            raise TextFileError(f"Папку не знайдено: {folder_path}")
        if not folder_path.is_dir():
            raise TextFileError(f"Вибраний шлях не є папкою: {folder_path}")
        for path in sorted(folder_path.iterdir(), key=lambda item: item.name.lower()):
            if path.is_file() and path.suffix.lower() == ".txt":
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    sources.append(path)

    return sources


def total_input_size(sources: Iterable[Path]) -> int:
    """Return total source byte size without modifying source files."""

    return sum(path.stat().st_size for path in sources)


def estimate_output_count(total_bytes: int, settings: DistributionSettings) -> int:
    """Estimate output file count from total bytes and mean chunk size."""

    if total_bytes <= 0:
        return 0
    return max(1, round(total_bytes / settings.mean_bytes))


def iter_utf8_text(sources: Iterable[Path], read_size: int = DEFAULT_READ_SIZE) -> Iterable[str]:
    """Yield decoded UTF-8 text chunks without loading all sources at once."""

    for source in sources:
        decoder = codecs.getincrementaldecoder("utf-8")(errors="ignore")
        with source.open("rb") as handle:
            while True:
                block = handle.read(read_size)
                if not block:
                    break
                text = decoder.decode(block)
                if text:
                    yield text
        tail = decoder.decode(b"", final=True)
        if tail:
            yield tail


def next_output_path(destination: Path, index: int) -> Path:
    return destination / f"{OUTPUT_FILE_PREFIX}_{index:06}.txt"


def build_size_distribution_report(
    generated_text_files: Iterable[Path],
    histogram_path: Union[str, Path],
    bucket_count: int = 10,
) -> SizeDistributionReport:
    """Write an SVG histogram and return summary statistics for generated text files."""

    paths = list(generated_text_files)
    if not paths:
        raise TextFileError("Немає файлів згенерованого тексту для діаграми.")
    if bucket_count <= 0:
        raise TextFileError("Кількість діапазонів гістограми має бути більшою за нуль.")

    sizes = [path.stat().st_size for path in paths]
    minimum = min(sizes)
    maximum = max(sizes)
    buckets = _build_histogram_buckets(sizes, minimum, maximum, bucket_count)
    output_path = Path(histogram_path)
    report = SizeDistributionReport(
        histogram_path=output_path,
        file_count=len(sizes),
        min_bytes=minimum,
        median_bytes=float(median(sizes)),
        mean_bytes=float(mean(sizes)),
        max_bytes=maximum,
        buckets=tuple(buckets),
    )
    _write_histogram_svg(report)
    return report


def write_generated_text_chunks(
    sources: Iterable[Path],
    destination: Union[str, Path],
    settings: DistributionSettings,
    progress_callback: Optional[ProgressCallback] = None,
) -> GenerationResult:
    """Write generated text chunk files until all source text is consumed."""

    source_list = list(sources)
    if not source_list:
        raise TextFileError("Виберіть хоча б один TXT файл-джерело.")

    settings.validate()
    destination_path = Path(destination)
    destination_path.mkdir(parents=True, exist_ok=True)
    total_bytes = total_input_size(source_list)
    output_index = 1
    output_bytes = 0
    generated_paths = []  # type: List[Path]
    target_bytes = sample_chunk_size_bytes(settings)
    current = bytearray()

    def flush_current() -> None:
        nonlocal current, output_index, output_bytes
        if not current:
            return
        output_path = next_output_path(destination_path, output_index)
        output_path.write_bytes(bytes(current))
        generated_paths.append(output_path)
        output_bytes += len(current)
        if progress_callback is not None:
            progress_callback(output_index, output_bytes, total_bytes, output_path)
        output_index += 1
        current = bytearray()

    for text in iter_utf8_text(source_list):
        for char in text:
            encoded = char.encode("utf-8")
            if current and len(current) + len(encoded) > target_bytes:
                flush_current()
                target_bytes = sample_chunk_size_bytes(settings)
            current.extend(encoded)

    flush_current()
    return GenerationResult(output_index - 1, output_bytes, destination_path, tuple(generated_paths))


def _build_histogram_buckets(
    sizes: List[int],
    minimum: int,
    maximum: int,
    bucket_count: int,
) -> List[HistogramBucket]:
    if minimum == maximum:
        return [HistogramBucket(minimum, maximum, len(sizes))]

    width = ceil((maximum - minimum + 1) / bucket_count)
    buckets = []  # type: List[HistogramBucket]
    for index in range(bucket_count):
        lower = minimum + index * width
        if lower > maximum:
            break
        upper = min(maximum, lower + width - 1)
        count = sum(1 for size in sizes if lower <= size <= upper)
        buckets.append(HistogramBucket(lower, upper, count))
    return buckets


def _write_histogram_svg(report: SizeDistributionReport) -> None:
    report.histogram_path.parent.mkdir(parents=True, exist_ok=True)
    width = 960
    height = 560
    left = 76
    right = 32
    top = 96
    bottom = 112
    chart_width = width - left - right
    chart_height = height - top - bottom
    max_count = max((bucket.count for bucket in report.buckets), default=1)
    bar_slot = chart_width / max(1, len(report.buckets))
    bar_width = max(20, bar_slot * 0.72)
    summary = (
        f"Файлів: {report.file_count} | Мін: {report.min_bytes} B | "
        f"Медіана: {_format_number(report.median_bytes)} B | "
        f"Середнє: {report.mean_bytes:.1f} B | Макс: {report.max_bytes} B"
    )
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<text x="76" y="42" fill="#111827" font-family="Inter, Arial, sans-serif" font-size="28" font-weight="700">Розподіл розмірів файлів згенерованого тексту</text>',
        f'<text x="76" y="72" fill="#475569" font-family="Inter, Arial, sans-serif" font-size="14">{escape(summary)}</text>',
        f'<line x1="{left}" y1="{top + chart_height}" x2="{left + chart_width}" y2="{top + chart_height}" stroke="#94a3b8" stroke-width="1"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_height}" stroke="#94a3b8" stroke-width="1"/>',
    ]
    for index, bucket in enumerate(report.buckets):
        x = left + index * bar_slot + (bar_slot - bar_width) / 2
        bar_height = 0 if max_count == 0 else (bucket.count / max_count) * chart_height
        y = top + chart_height - bar_height
        label = f"{bucket.lower}-{bucket.upper}"
        elements.extend(
            [
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="6" fill="#7c3aed"/>',
                f'<text x="{x + bar_width / 2:.1f}" y="{max(22, y - 8):.1f}" text-anchor="middle" fill="#312e81" font-family="Inter, Arial, sans-serif" font-size="13" font-weight="700">{bucket.count}</text>',
                f'<text x="{x + bar_width / 2:.1f}" y="{top + chart_height + 28}" text-anchor="middle" fill="#334155" font-family="Inter, Arial, sans-serif" font-size="11" transform="rotate(35 {x + bar_width / 2:.1f} {top + chart_height + 28})">{escape(label)}</text>',
            ]
        )
    elements.append("</svg>")
    report.histogram_path.write_text("\n".join(elements), encoding="utf-8")


def _format_number(value: float) -> str:
    return str(int(value)) if value.is_integer() else f"{value:.1f}"
