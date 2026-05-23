from pathlib import Path
from typing import List, Optional, Tuple

import pytest

from file_configurator import generated_text_splitter
from file_configurator.generated_text_splitter import (
    BYTES_PER_KB,
    DistributionSettings,
    HistogramBucket,
    build_size_distribution_report,
    collect_txt_sources,
    estimate_output_count,
    next_output_path,
    sample_chunk_size_bytes,
    total_input_size,
    write_generated_text_chunks,
)
from file_configurator.text_file import TextFileError


def test_default_distribution_uses_mean_and_std_settings() -> None:
    settings = DistributionSettings()

    assert settings.mean_kb == 2.5
    assert settings.std_kb == 1.0
    assert settings.mean_bytes == round(2.5 * BYTES_PER_KB)
    assert estimate_output_count(10 * BYTES_PER_KB, settings) == 4


def test_sample_chunk_size_bytes_generates_positive_sizes() -> None:
    settings = DistributionSettings(mean_kb=2.5, std_kb=1.0)

    samples = [sample_chunk_size_bytes(settings, random_state=seed) for seed in range(100)]

    assert all(sample >= 1 for sample in samples)


def test_sample_chunk_size_bytes_resamples_non_positive_values(monkeypatch) -> None:
    class FakeDistribution:
        def __init__(self) -> None:
            self.samples = iter([-2.0, 0.0, 1.25])

        def rvs(self, random_state: Optional[object] = None) -> float:
            return next(self.samples)

    fake_distribution = FakeDistribution()
    monkeypatch.setattr(generated_text_splitter, "norm", lambda loc, scale: fake_distribution)

    assert sample_chunk_size_bytes(DistributionSettings(mean_kb=6.0, std_kb=2.0)) == round(1.25 * BYTES_PER_KB)


@pytest.mark.parametrize(
    "settings",
    [
        DistributionSettings(mean_kb=0),
        DistributionSettings(mean_kb=-1),
        DistributionSettings(std_kb=0),
    ],
)
def test_distribution_settings_reject_invalid_values(settings: DistributionSettings) -> None:
    with pytest.raises(TextFileError):
        settings.validate()


def test_collect_txt_sources_accepts_selected_files_and_top_level_folder_txt(tmp_path: Path) -> None:
    selected = tmp_path / "selected.txt"
    first = tmp_path / "a.TXT"
    second = tmp_path / "b.txt"
    ignored = tmp_path / "notes.md"
    nested = tmp_path / "nested"
    nested_file = nested / "nested.txt"
    for path in (selected, first, second, ignored):
        path.write_text(path.name, encoding="utf-8")
    nested.mkdir()
    nested_file.write_text("nested", encoding="utf-8")

    sources = collect_txt_sources([selected, ignored, selected], folder=tmp_path)

    assert [path.name for path in sources] == ["selected.txt", "a.TXT", "b.txt"]


def test_total_input_size_does_not_modify_sources(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("абв", encoding="utf-8")
    before = source.read_bytes()

    assert total_input_size([source]) == len(before)
    assert source.read_bytes() == before


def test_next_output_path_uses_sequential_generated_text_names(tmp_path: Path) -> None:
    assert next_output_path(tmp_path, 1) == tmp_path / "generated_text_000001.txt"
    assert next_output_path(tmp_path, 42) == tmp_path / "generated_text_000042.txt"


def test_write_generated_text_chunks_preserves_sources_and_consumes_all_input(
    tmp_path: Path,
    monkeypatch,
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("аб", encoding="utf-8")
    second.write_text("cd", encoding="utf-8")
    before = {first: first.read_bytes(), second: second.read_bytes()}
    destination = tmp_path / "out"
    targets = iter([4, 2])
    progress = []  # type: List[Tuple[int, int, int, str]]
    monkeypatch.setattr(generated_text_splitter, "sample_chunk_size_bytes", lambda settings: next(targets))

    result = write_generated_text_chunks(
        [first, second],
        destination,
        DistributionSettings(),
        progress_callback=lambda count, output_bytes, total_bytes, path: progress.append(
            (count, output_bytes, total_bytes, path.name)
        ),
    )

    generated = sorted(destination.glob("generated_text_*.txt"))
    generated_bytes = b"".join(path.read_bytes() for path in generated)
    expected_bytes = before[first] + before[second]
    assert [path.name for path in generated] == ["generated_text_000001.txt", "generated_text_000002.txt"]
    assert generated_bytes == expected_bytes
    assert first.read_bytes() == before[first]
    assert second.read_bytes() == before[second]
    assert result.generated_files == 2
    assert result.output_bytes == len(expected_bytes)
    assert result.destination == destination
    assert result.generated_paths == tuple(generated)
    assert progress == [
        (1, len(before[first]), len(expected_bytes), "generated_text_000001.txt"),
        (2, len(expected_bytes), len(expected_bytes), "generated_text_000002.txt"),
    ]


def test_write_generated_text_chunks_never_splits_utf8_character(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "source.txt"
    source.write_text("aєb", encoding="utf-8")
    destination = tmp_path / "out"
    targets = iter([2, 2, 2])
    monkeypatch.setattr(generated_text_splitter, "sample_chunk_size_bytes", lambda settings: next(targets))

    write_generated_text_chunks([source], destination, DistributionSettings())

    payloads = [path.read_bytes() for path in sorted(destination.glob("generated_text_*.txt"))]
    assert payloads == [b"a", "є".encode("utf-8"), b"b"]
    assert b"".join(payloads) == source.read_bytes()
    for payload in payloads:
        payload.decode("utf-8")


def test_write_generated_text_chunks_requires_sources(tmp_path: Path) -> None:
    with pytest.raises(TextFileError, match="хоча б один TXT"):
        write_generated_text_chunks([], tmp_path / "out", DistributionSettings())


def test_build_size_distribution_report_writes_svg_and_text_summary(tmp_path: Path) -> None:
    sizes = [1150, 2048, 2049, 10132]
    generated_text_files = []
    for index, size in enumerate(sizes, start=1):
        path = tmp_path / f"generated_text_{index:06}.txt"
        path.write_bytes(b"x" * size)
        generated_text_files.append(path)
    histogram_path = tmp_path / "generated_text_sizes_histogram.svg"

    report = build_size_distribution_report(generated_text_files, histogram_path)

    assert histogram_path.exists()
    assert "<svg" in histogram_path.read_text(encoding="utf-8")
    assert report.file_count == 4
    assert report.min_bytes == 1150
    assert report.median_bytes == 2048.5
    assert report.mean_bytes == pytest.approx(3844.75)
    assert report.max_bytes == 10132
    assert report.buckets[0] == HistogramBucket(1150, 2048, 2)
    assert report.buckets[1] == HistogramBucket(2049, 2947, 1)
    assert report.buckets[-1] == HistogramBucket(9241, 10132, 1)
    text = report.to_text()
    assert "Згенеровано діаграму розподілу розмірів файлів згенерованого тексту" in text
    assert str(histogram_path) in text
    assert "- Файлів: 4" in text
    assert "- Медіана: 2048.5 B" in text
    assert "- Середнє: 3844.8 B" in text
    assert "Текстовий вигляд розподілу:" in text


def test_build_size_distribution_report_requires_generated_files(tmp_path: Path) -> None:
    with pytest.raises(TextFileError, match="Немає файлів згенерованого тексту"):
        build_size_distribution_report([], tmp_path / "generated_text_sizes_histogram.svg")
