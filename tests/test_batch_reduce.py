from pathlib import Path

import pytest

from file_configurator.batch_reduce import (
    BYTES_PER_KB,
    BYTES_PER_MB,
    expand_utf8_bytes,
    generate_random_utf8_padding,
    reduce_text_files,
    reduce_folder_text_files,
    scan_batch_target,
    scan_batch_folder,
    target_size_to_bytes,
    target_size_kb_to_bytes,
    truncate_utf8_to_bytes,
)
from file_configurator.tiny_text_model import TINY_LANGUAGE_CORPUS, TinyCharacterModel
from file_configurator.text_file import TextFileError


@pytest.mark.parametrize(("value", "expected"), [(1, 1024), (20, 20 * BYTES_PER_KB), (" 2 ", 2 * BYTES_PER_KB)])
def test_target_size_kb_to_bytes_accepts_positive_integer_values(value: int | str, expected: int) -> None:
    assert target_size_kb_to_bytes(value) == expected


@pytest.mark.parametrize(("value", "unit", "expected"), [(512, "B", 512), (2, "KB", 2 * BYTES_PER_KB), (3, "MB", 3 * BYTES_PER_MB)])
def test_target_size_to_bytes_supports_units(value: int, unit: str, expected: int) -> None:
    assert target_size_to_bytes(value, unit) == expected


@pytest.mark.parametrize("value", [0, -1, "", "0", "-1", "1.5", "abc", True])
def test_target_size_kb_to_bytes_rejects_invalid_values(value: int | str | bool) -> None:
    with pytest.raises(TextFileError, match="додатним цілим"):
        target_size_kb_to_bytes(value)


def test_target_size_to_bytes_rejects_invalid_unit() -> None:
    with pytest.raises(TextFileError, match="підтримувану одиницю"):
        target_size_to_bytes(1, "GB")


def test_truncate_utf8_to_bytes_reduces_ascii_to_target_size() -> None:
    assert truncate_utf8_to_bytes("abcdef", 3) == "abc"


def test_truncate_utf8_to_bytes_preserves_valid_multibyte_text() -> None:
    result = truncate_utf8_to_bytes("\u00e9\u00e9\u00e9", 3)

    assert result == "\u00e9"
    assert len(result.encode("utf-8")) <= 3


def test_expand_utf8_bytes_generates_random_valid_utf8_padding() -> None:
    result = expand_utf8_bytes("abc".encode("utf-8"), 10)

    assert result.startswith(b"abc")
    assert len(result) == 10
    result.decode("utf-8")


def test_random_padding_looks_like_language_text() -> None:
    text = generate_random_utf8_padding(300).decode("utf-8").lower()

    assert any("а" <= char <= "я" or char in "іїєґ" for char in text)
    assert " " in text


def test_tiny_character_model_generates_exact_sized_language_like_padding() -> None:
    model = TinyCharacterModel(TINY_LANGUAGE_CORPUS)
    text = model.generate(150)

    assert len(text.encode("utf-8")) >= 150
    assert any("а" <= char.lower() <= "я" or char.lower() in "іїєґ" for char in text)


def test_scan_batch_folder_selects_top_level_txt_and_skips_other_entries(tmp_path: Path) -> None:
    first = tmp_path / "a.txt"
    second = tmp_path / "b.TXT"
    unsupported = tmp_path / "image.png"
    subfolder = tmp_path / "nested"
    first.write_text("a", encoding="utf-8")
    second.write_text("b", encoding="utf-8")
    unsupported.write_text("x", encoding="utf-8")
    subfolder.mkdir()

    txt_files, skipped = scan_batch_folder(tmp_path)

    assert [path.name for path in txt_files] == ["a.txt", "b.TXT"]
    reasons = {item.path.name: item.reason for item in skipped}
    assert reasons == {
        "image.png": "Непідтримуваний тип файлу пропущено.",
        "nested": "Підпапку пропущено.",
    }


def test_scan_batch_target_accepts_single_txt_file(tmp_path: Path) -> None:
    path = tmp_path / "single.txt"
    path.write_text("content", encoding="utf-8")

    txt_files, skipped = scan_batch_target(path)

    assert txt_files == [path]
    assert skipped == []


def test_scan_batch_target_skips_single_unsupported_file(tmp_path: Path) -> None:
    path = tmp_path / "single.csv"
    path.write_text("content", encoding="utf-8")

    txt_files, skipped = scan_batch_target(path)

    assert txt_files == []
    assert [item.path for item in skipped] == [path]


def test_reduce_folder_text_files_reduces_large_files_and_skips_smaller_entries(tmp_path: Path) -> None:
    big = tmp_path / "big.txt"
    small = tmp_path / "small.txt"
    unsupported = tmp_path / "notes.md"
    subfolder = tmp_path / "nested"
    big.write_text("a" * 2048, encoding="utf-8")
    small.write_text("small", encoding="utf-8")
    unsupported.write_text("unsupported", encoding="utf-8")
    subfolder.mkdir()

    result = reduce_folder_text_files(tmp_path, 1)

    assert [item.path.name for item in result.reduced] == ["big.txt"]
    assert big.stat().st_size <= BYTES_PER_KB
    assert small.read_text(encoding="utf-8") == "small"
    skipped_reasons = {item.path.name: item.reason for item in result.skipped}
    assert skipped_reasons["small.txt"] == "Файл уже не перевищує цільовий розмір."
    assert skipped_reasons["notes.md"] == "Непідтримуваний тип файлу пропущено."
    assert skipped_reasons["nested"] == "Підпапку пропущено."
    assert result.failed == []


def test_reduce_folder_text_files_continues_after_individual_file_failure(tmp_path: Path) -> None:
    bad = tmp_path / "bad.txt"
    good = tmp_path / "good.txt"
    bad.write_bytes(b"\xff" * 2048)
    good.write_text("g" * 2048, encoding="utf-8")

    result = reduce_folder_text_files(tmp_path, 1)

    assert [item.path.name for item in result.failed] == ["bad.txt"]
    assert [item.path.name for item in result.reduced] == ["good.txt"]
    assert good.stat().st_size <= BYTES_PER_KB


def test_reduce_text_files_reduces_single_selected_file_with_byte_unit(tmp_path: Path) -> None:
    path = tmp_path / "big.txt"
    path.write_text("abcdef", encoding="utf-8")

    result = reduce_text_files(path, 3, "B")

    assert [item.path.name for item in result.reduced] == ["big.txt"]
    assert path.read_text(encoding="utf-8") == "abc"


def test_reduce_text_files_keeps_smaller_single_file_unchanged(tmp_path: Path) -> None:
    path = tmp_path / "small.txt"
    path.write_text("small", encoding="utf-8")

    result = reduce_text_files(path, 20, "KB")

    assert result.reduced == []
    assert [item.path.name for item in result.skipped] == ["small.txt"]
    assert path.read_text(encoding="utf-8") == "small"


def test_reduce_text_files_can_expand_smaller_single_file_to_target(tmp_path: Path) -> None:
    path = tmp_path / "small.txt"
    path.write_text("small", encoding="utf-8")

    result = reduce_text_files(path, 20, "B", fill_smaller=True)

    data = path.read_bytes()
    assert result.reduced == []
    assert [item.path.name for item in result.expanded] == ["small.txt"]
    assert data.startswith(b"small")
    assert len(data) == 20
    data.decode("utf-8")


def test_reduce_text_files_can_expand_smaller_folder_files_when_enabled(tmp_path: Path) -> None:
    small = tmp_path / "small.txt"
    exact = tmp_path / "exact.txt"
    small.write_text("abc", encoding="utf-8")
    exact.write_text("12345", encoding="utf-8")

    result = reduce_text_files(tmp_path, 5, "B", fill_smaller=True)

    assert [item.path.name for item in result.expanded] == ["small.txt"]
    assert [item.path.name for item in result.skipped] == ["exact.txt"]
    assert small.stat().st_size == 5
    assert exact.read_text(encoding="utf-8") == "12345"


def test_reduce_text_files_reports_progress_for_each_txt_file(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("a" * 10, encoding="utf-8")
    second.write_text("b" * 10, encoding="utf-8")
    progress: list[tuple[int, int, str]] = []

    reduce_text_files(
        tmp_path,
        5,
        "B",
        progress_callback=lambda current, total, path: progress.append((current, total, path.name)),
    )

    assert progress == [(1, 2, "first.txt"), (2, 2, "second.txt")]
