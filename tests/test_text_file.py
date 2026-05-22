from pathlib import Path

import pytest

from file_configurator.text_file import (
    TextFileError,
    read_text_file,
    validate_txt_path,
    write_text_file,
)


def test_validate_txt_path_accepts_txt_extension(tmp_path: Path) -> None:
    path = tmp_path / "notes.TXT"

    assert validate_txt_path(path) == path


def test_validate_txt_path_rejects_other_extensions(tmp_path: Path) -> None:
    with pytest.raises(TextFileError, match=r"Only \.txt files"):
        validate_txt_path(tmp_path / "notes.md")


def test_validate_txt_path_rejects_empty_selection() -> None:
    with pytest.raises(TextFileError, match="No file path"):
        validate_txt_path("")


def test_write_and_read_text_file_uses_utf8(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    content = "plain text with caf\u00e9"

    assert write_text_file(path, content) == path

    assert read_text_file(path) == content


def test_read_text_file_reports_missing_file(tmp_path: Path) -> None:
    with pytest.raises(TextFileError, match="File not found"):
        read_text_file(tmp_path / "missing.txt")


def test_read_text_file_reports_decode_error(tmp_path: Path) -> None:
    path = tmp_path / "broken.txt"
    path.write_bytes(b"\xff")

    with pytest.raises(TextFileError, match="UTF-8"):
        read_text_file(path)


def test_write_text_file_rejects_non_txt_path(tmp_path: Path) -> None:
    with pytest.raises(TextFileError, match=r"Only \.txt files"):
        write_text_file(tmp_path / "notes.log", "content")
