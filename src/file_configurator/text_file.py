"""Helpers for reading and writing supported text files."""

from pathlib import Path
from typing import Union


class TextFileError(Exception):
    """Raised when a supported text-file operation cannot be completed."""


def validate_txt_path(path: Union[str, Path]) -> Path:
    """Return a normalized path when it points to a supported .txt file."""

    if not path:
        raise TextFileError("No file path was selected.")

    txt_path = Path(path)
    if txt_path.suffix.lower() != ".txt":
        raise TextFileError("Only .txt files are supported.")

    return txt_path


def read_text_file(path: Union[str, Path]) -> str:
    """Read a UTF-8 .txt file."""

    txt_path = validate_txt_path(path)
    try:
        return txt_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TextFileError(f"File not found: {txt_path}") from exc
    except UnicodeDecodeError as exc:
        raise TextFileError(f"Could not read {txt_path.name} as UTF-8 text.") from exc
    except OSError as exc:
        raise TextFileError(f"Could not read {txt_path}: {exc}") from exc


def write_text_file(path: Union[str, Path], content: str) -> Path:
    """Write UTF-8 text to a supported .txt file and return its path."""

    txt_path = validate_txt_path(path)
    try:
        txt_path.write_text(content, encoding="utf-8")
    except UnicodeEncodeError as exc:
        raise TextFileError(f"Could not encode {txt_path.name} as UTF-8 text.") from exc
    except OSError as exc:
        raise TextFileError(f"Could not write {txt_path}: {exc}") from exc

    return txt_path
