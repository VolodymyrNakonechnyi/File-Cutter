## Why

Users need a focused file utility for reducing `.txt` file sizes instead of a text editor. Adding a Ukrainian file-only interface and folder-based batch size reduction makes the app useful for quickly normalizing large text files to a chosen target size.

## What Changes

- Add a file-or-folder selection workflow for choosing one `.txt` file or a directory of `.txt` files.
- Add a user-controlled target size with `B`, `KB`, and `MB` units, such as reducing files from about 200 KB down to 20 KB.
- Process each supported file in the selected folder and reduce files larger than the target size to that target size.
- Add an optional mode that fills smaller `.txt` files with language-like randomized text from a tiny built-in character model until they reach the target size.
- Show progress while files are being processed.
- Report batch results, including processed files, skipped files, and failures.
- Replace the single-file editor UI with a focused Ukrainian file-operations UI.
- Add generated mock `.txt` files for testing with many 100 KB and 200 KB examples.

## Capabilities

### New Capabilities

### Modified Capabilities
- `txt-file-workspace`: Add file-or-folder batch reduction for `.txt` files, support multiple size units, localize the app UI to Ukrainian, and remove the single-file editor workflow from the UI.

## Impact

- Affects the PySide6 main window by replacing editor controls with Ukrainian folder selection, target-size input, and batch progress/results UI.
- Extends text-file services with directory scanning and size-reduction logic.
- Requires tests for size validation, batch processing, truncation behavior, skipped files, and error reporting.
- Adds generated local mock data under `mock_txt_files/` for manual testing.
