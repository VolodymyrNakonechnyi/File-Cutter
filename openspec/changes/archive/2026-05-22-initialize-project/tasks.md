## 1. Project Scaffold

- [x] 1.1 Add `pyproject.toml` with package metadata, Python version, PySide6 dependency, pytest dependency, and a Windows-compatible console entry point for launching the app.
- [x] 1.2 Create the `src/file_configurator` package with an application entry point that initializes the Qt application and main window.
- [x] 1.3 Add basic repository files such as `.gitignore` and `README.md` with Windows setup, run, and verification commands.

## 2. Text File Services

- [x] 2.1 Implement `.txt` path validation that accepts only files with a `.txt` extension.
- [x] 2.2 Implement UTF-8 read and write helpers for text-file content.
- [x] 2.3 Return clear errors from file operations so the UI can inform the user without crashing.

## 3. Desktop UI

- [x] 3.1 Build the main window with a plain text editor, file menu actions, and status/title updates.
- [x] 3.2 Wire New, Open, Save, Save As, and Exit actions to the text-file services.
- [x] 3.3 Restrict open and save dialogs to `.txt` files and validate selected paths before file operations.
- [x] 3.4 Track dirty state and prompt the user to save, discard, or cancel before losing unsaved edits.
- [x] 3.5 Display user-facing error messages for unsupported paths and file read/write failures.

## 4. Verification

- [x] 4.1 Add pytest coverage for `.txt` validation and text-file read/write helpers.
- [x] 4.2 Add a lightweight import or entry-point smoke check that does not require long-running GUI interaction.
- [x] 4.3 Run the documented Windows verification commands and confirm the application launch path is documented.
