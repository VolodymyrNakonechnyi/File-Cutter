## 1. Dependencies And Cleanup

- [x] 1.1 Add SciPy as a runtime dependency in project metadata.
- [x] 1.2 Remove or stop exposing the old size reduction, fill, and tiny filler model workflow from the main application path.
- [x] 1.3 Keep package entry points intact so `python -m file_configurator` launches the rewritten app.

## 2. Distribution Service

- [x] 2.1 Add a distribution settings model with mean KB and std KB validation.
- [x] 2.2 Implement SciPy `norm` chunk-size sampling using the configured mean and standard deviation.
- [x] 2.3 Reject non-positive sampled KB values and convert positive samples to byte targets with a minimum emitted chunk size of 1 byte.
- [x] 2.4 Add tests proving sampled sizes are positive, non-positive samples are retried, and defaults match generated text chunks.

## 3. Source And Slicing Services

- [x] 3.1 Implement source selection helpers for multiple `.txt` files and top-level `.txt` files from a selected folder.
- [x] 3.2 Implement total input size calculation without modifying source files.
- [x] 3.3 Implement UTF-8-safe byte slicing that consumes source text sequentially and never writes invalid UTF-8.
- [x] 3.4 Implement output naming as `generated_text_000001.txt`, `generated_text_000002.txt`, and so on in the selected destination folder.
- [x] 3.5 Implement generation progress reporting based on consumed bytes or generated output count.
- [x] 3.6 Add tests for source preservation, UTF-8 slicing, output naming, and generation until input exhaustion.

## 4. Ukrainian UI Rewrite

- [x] 4.1 Replace the current main window with a generated-text-splitting UI in Ukrainian.
- [x] 4.2 Add controls for selecting source TXT files and a source folder.
- [x] 4.3 Add destination folder selection and validation.
- [x] 4.4 Add numeric controls for mean KB and std KB with generated text defaults.
- [x] 4.5 Add a preview showing total source size and estimated output file count.
- [x] 4.6 Add a prominent `Згенерувати текстові файли` action button.
- [x] 4.7 Add progress bar updates and compact completion summary.

## 5. Documentation And Verification

- [x] 5.1 Rewrite README to describe the generated-text splitting workflow, SciPy dependency, distribution settings, and destination output behavior.
- [x] 5.2 Update or replace tests that are tied to the old resize/fill behavior.
- [x] 5.3 Run the full test suite.
- [x] 5.4 Run the import smoke check for the rewritten application.

## 6. Generated Size Distribution Report

- [x] 6.1 Track the generated text file paths for post-generation reporting.
- [x] 6.2 Generate `generated_text_sizes_histogram.svg` from generated text file sizes.
- [x] 6.3 Include file count, min, median, mean, max, and textual histogram in the completion UI.
- [x] 6.4 Add tests and documentation for the generated distribution report.

## 7. Python 3.6 Compatibility

- [x] 7.1 Move packaging metadata to Python 3.6-compatible `setup.cfg` metadata.
- [x] 7.2 Add Python-version-specific dependency pins for PySide2/PySide6, SciPy, pytest, and dataclasses.
- [x] 7.3 Remove Python 3.7+ syntax and Python 3.8+ syntax from importable source modules.
- [x] 7.4 Add PySide2 fallback imports for Python 3.6 compatible Qt installs.
