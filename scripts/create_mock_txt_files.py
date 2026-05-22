"""Generate local mock TXT files for manual reduction testing."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "mock_txt_files"
BYTES_PER_KB = 1024


def write_mock_file(path: Path, size_kb: int) -> None:
    pattern = (f"{path.stem} mock content line for reduction testing.\n").encode("utf-8")
    target_size = size_kb * BYTES_PER_KB
    repeats = (target_size // len(pattern)) + 1
    path.write_bytes((pattern * repeats)[:target_size])


def main() -> int:
    OUTPUT_DIR.mkdir(exist_ok=True)

    for index in range(1, 51):
        write_mock_file(OUTPUT_DIR / f"mock_100kb_{index:03}.txt", 100)

    for index in range(1, 51):
        write_mock_file(OUTPUT_DIR / f"mock_200kb_{index:03}.txt", 200)

    for index in range(1, 11):
        write_mock_file(OUTPUT_DIR / f"mock_10kb_{index:03}.txt", 10)

    print(f"Created 110 mock TXT files in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
