## Context

The current app includes single `.txt` document creation, opening, editing, and saving. Users now need a focused file utility where they select either one file or a folder and reduce every supported target file to a chosen size, such as reducing 200 KB text files to 20 KB.

This operation is destructive because it overwrites file contents with shortened content, so the design must make scope, validation, and results clear before and after processing. The UI should be Ukrainian because the target user-facing workflow is Ukrainian.

## Goals / Non-Goals

**Goals:**
- Let the user select a `.txt` file or folder and enter a numeric target size.
- Support size units beyond KB: bytes, KB, and MB.
- Reduce `.txt` files larger than the target size without affecting smaller `.txt` files.
- Optionally expand smaller `.txt` files with language-like randomized valid text from a tiny built-in character model until they reach the target size.
- Show file processing progress in the UI.
- Ensure users can only enter numeric size values.
- Provide generated mock files for manual testing with 100 KB and 200 KB `.txt` files.
- Keep UTF-8 output valid after truncation.
- Show a confirmation before overwriting files and a results summary after processing.
- Replace editor controls with a file-operations-only Ukrainian interface.

**Non-Goals:**
- Process non-`.txt` files, subfolders, compressed archives, or binary files.
- Add automatic backups, undo, or version history.
- Preserve semantic document structure when truncating content.
- Continue offering single-file editing actions in the UI.
- Add asynchronous background processing unless the UI becomes unresponsive during implementation testing.

## Decisions

- Process one selected `.txt` file or top-level `.txt` files in the selected folder.
  - Rationale: The request describes all files in a selected folder, and limiting scope avoids accidentally modifying nested directories.
  - Alternative considered: Recursive processing. That is more powerful but riskier for a destructive batch operation.

- Interpret size input as a positive integer with a selected unit: `B`, `KB`, or `MB`, where binary units use `1024` multipliers.
  - Rationale: Users asked to work beyond kilobytes while still entering only numeric data.
  - Alternative considered: Free-form text such as `20kb`. That is more flexible but violates the numeric-only input requirement.

- Reduce size by UTF-8-safe truncation.
  - Rationale: The existing app is a `.txt` editor, and truncation is the direct way to make a text file smaller while preserving valid UTF-8 output.
  - Alternative considered: Compressing files. Compression changes file format and does not keep the files as editable `.txt` files.

- Keep smaller-file expansion opt-in and generate language-like text.
  - Rationale: Users may only want to shrink oversized files, so smaller files must stay unchanged unless the user explicitly enables randomized fill.
  - Alternative considered: Always fill smaller files or use character noise. That would unexpectedly modify files by default and produce unreadable content.

- Use a dependency-free toy character model instead of a real ML runtime.
  - Rationale: The requested model should be maximally small; PyTorch/TensorFlow and downloaded weights would be much larger than the application.
  - Alternative considered: Ship a real trained language model. That would add large dependencies and model files for a feature that only needs filler text.

- Report progress after each target `.txt` file is processed.
  - Rationale: Large folders can take noticeable time, so users need visible progress instead of a frozen-looking window.
  - Alternative considered: Only show final results. That is simpler but gives no feedback during long operations.

- Overwrite files in place after explicit confirmation.
  - Rationale: The user asked to resize all files in the folder, and in-place writes keep the workflow simple.
  - Alternative considered: Write reduced copies to another folder. Safer, but adds destination management and does not match the direct resize request.

- Return structured batch results from the service layer.
  - Rationale: The UI needs to report processed, skipped, and failed files without duplicating file-processing logic.
  - Alternative considered: Have the UI loop over files directly. That would mix destructive file logic into the window and make it harder to test.

- Remove the text editor from the main window and localize visible UI strings to Ukrainian.
  - Rationale: The app should be a file utility for actions like shortening files, not a document editor.
  - Alternative considered: Keep both editor and batch controls. That creates a mixed-purpose UI and conflicts with the file-only direction.

- Generate local mock files through a script instead of hand-maintaining large fixture contents.
  - Rationale: A script can reliably create many 100 KB and 200 KB files without bloating source patches.
  - Alternative considered: Commit many static files. That makes the repository noisy and harder to maintain.

## Risks / Trade-offs

- Data loss from truncation -> Show a confirmation that files will be overwritten and document that the operation is destructive.
- UTF-8 files with multibyte characters may end slightly under the requested byte size -> Prefer valid text over invalid byte-perfect truncation.
- Large folders may briefly block the UI -> Keep initial implementation simple, but structure batch processing so it can move to a worker thread later.
- Users may expect non-`.txt` files to be processed -> Keep filters and results explicit about skipped unsupported files.
- Mock files can take disk space -> Keep them in a dedicated `mock_txt_files/` folder and make regeneration explicit.
- Random fill changes file contents destructively -> Keep the fill option unchecked by default, generate text that looks like sentences, and explain it in the confirmation prompt.

## Migration Plan

1. Add reusable file-or-folder reduction services and tests.
2. Replace the editor UI with Ukrainian controls/actions for file/folder selection, numeric size entry, unit selection, confirmation, and results display.
3. Add mock file generation and update documentation with the destructive nature and supported scope of batch reduction.
4. Rollback is restoring the old editor window and removing the new batch UI/service code.

## Open Questions

- None for the initial version. Recursive processing and backup output folders can be proposed separately if users need them.
