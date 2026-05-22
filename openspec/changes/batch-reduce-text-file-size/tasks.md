## 1. Batch Service Layer

- [x] 1.1 Add a batch result model that tracks reduced, skipped, and failed files with user-readable reasons.
- [x] 1.2 Add target-size validation that accepts positive integer KB values and converts them to bytes using `1 KB = 1024 bytes`.
- [x] 1.3 Add folder scanning for top-level entries that selects `.txt` files and classifies unsupported files and subfolders as skipped.
- [x] 1.4 Add UTF-8-safe truncation that reduces oversized text content to no more than the target byte size without writing invalid UTF-8.
- [x] 1.5 Add batch processing that overwrites oversized `.txt` files in place, skips files already within target size, records per-file failures, and continues processing.

## 2. Windows UI Workflow

- [x] 2.1 Add a batch reduction action or section to the main window without disrupting the existing single-file editor actions.
- [x] 2.2 Add folder selection using a Windows folder picker and display the selected folder to the user.
- [x] 2.3 Add target-size input in KB and show validation errors before processing.
- [x] 2.4 Add a destructive confirmation prompt before any batch file writes begin.
- [x] 2.5 Run the batch service from the UI and display a completion summary with reduced, skipped, and failed counts.
- [x] 2.6 Surface detailed failure and skipped-file reasons in a readable results message.

## 3. Tests And Documentation

- [x] 3.1 Add unit tests for target-size validation and KB-to-byte conversion.
- [x] 3.2 Add unit tests for UTF-8-safe truncation, including multibyte characters.
- [x] 3.3 Add unit tests for folder scanning, skipped unsupported files, skipped subfolders, and skipped smaller `.txt` files.
- [x] 3.4 Add unit tests for batch processing continuing after individual file failures.
- [x] 3.5 Update Windows documentation to describe folder batch reduction, destructive overwrite behavior, supported `.txt` scope, and verification commands.
- [x] 3.6 Run the test suite and confirm existing single-file workflows remain covered.

## 4. Ukrainian File-Only UI Update

- [x] 4.1 Replace the editor-centered main window with a focused batch file operations window.
- [x] 4.2 Translate user-visible labels, buttons, prompts, titles, and status messages to Ukrainian.
- [x] 4.3 Update documentation to describe the app as a Ukrainian `.txt` file reduction utility.
- [x] 4.4 Run the test suite and import smoke check after the UI change.

## 5. File Selection, Units, And Mock Data Update

- [x] 5.1 Add service support for reducing either one selected `.txt` file or top-level `.txt` files in a selected folder.
- [x] 5.2 Add service support for target units `B`, `KB`, and `MB` while preserving numeric-only size validation.
- [x] 5.3 Update the UI to choose either a single TXT file or a folder.
- [x] 5.4 Update the UI to use a numeric-only size field plus a non-editable unit selector.
- [x] 5.5 Add a script and generated `mock_txt_files/` folder with many 100 KB and 200 KB test files.
- [x] 5.6 Update tests and documentation for file selection, units, smaller-file preservation, and mock-file generation.
- [x] 5.7 Run the test suite and import smoke check after the update.

## 6. Optional Random Fill Update

- [x] 6.1 Update specs and design for optional randomized fill of smaller files.
- [x] 6.2 Add service support for opt-in randomized fill while keeping default smaller-file preservation.
- [x] 6.3 Add a Ukrainian checkbox and confirmation text for randomized fill.
- [x] 6.4 Add tests and documentation for randomized fill behavior.
- [x] 6.5 Run the test suite and import smoke check after the update.

## 7. Progress And Language-Like Fill Update

- [x] 7.1 Add progress reporting from the file processing service.
- [x] 7.2 Add a Ukrainian progress bar to the UI that updates as each file finishes.
- [x] 7.3 Replace character-noise random fill with language-like generated text.
- [x] 7.4 Update tests and documentation for progress and language-like fill.
- [x] 7.5 Run the test suite and import smoke check after the update.

## 8. Completion UX Update

- [x] 8.1 Replace the full detailed completion popup with a compact summary popup.
- [x] 8.2 Make the processing start button visually prominent and clearly labeled.
- [x] 8.3 Run the test suite and import smoke check after the completion UX update.

## 9. Tiny Text Model Update

- [x] 9.1 Add a tiny dependency-free character model for filler text generation.
- [x] 9.2 Wire smaller-file fill to the tiny model instead of direct word sampling.
- [x] 9.3 Update tests and documentation for the tiny model behavior.
- [x] 9.4 Run the test suite and import smoke check after the tiny model update.
