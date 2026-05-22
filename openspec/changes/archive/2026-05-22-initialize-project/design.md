## Context

The repository is currently empty except for OpenSpec change metadata. This change initializes a Windows Python desktop application for working with `.txt` files and needs to establish the first source layout, dependency choice, launch path, and validation approach.

The app should be small enough to implement quickly while leaving clear seams for future text-file configuration features.

## Goals / Non-Goals

**Goals:**
- Create a runnable Windows Python Qt desktop application from a fresh checkout.
- Support the initial `.txt` workflow: new file, open file, edit text, save, and save as.
- Keep file I/O and UI wiring separated enough to test text-file behavior without launching the GUI.
- Add minimal project documentation and verification commands.

**Non-Goals:**
- Add rich text editing, syntax highlighting, tabs, project folders, or binary file handling.
- Add packaging installers or support for non-Windows operating systems.
- Add persistence beyond normal filesystem reads and writes.

## Decisions

- Use `src/file_configurator` as the Python package layout.
  - Rationale: The `src` layout prevents accidental imports from the repository root and keeps implementation code separate from tests and OpenSpec artifacts.
  - Alternative considered: A flat package at the repository root. This is simpler but scales poorly as UI, services, and tests are added.

- Use PySide6 as the default Qt binding.
  - Rationale: PySide6 is the official Qt for Python binding, installs from PyPI, and is suitable for a small Windows desktop scaffold.
  - Alternative considered: PyQt6. It is also capable, but PySide6 provides a clearer default for a newly initialized project unless a PyQt-specific requirement appears.

- Keep document operations in a small service module separate from widgets.
  - Rationale: Opening, validating, reading, and writing `.txt` files can be tested with pytest without requiring a display server.
  - Alternative considered: Put all logic in the main window. That is faster initially but makes file behavior harder to verify and maintain.

- Treat UTF-8 as the default text encoding and surface failures to the user.
  - Rationale: UTF-8 is the safest modern default for `.txt` workflows. Decode or write failures should not crash the app.
  - Alternative considered: Detect encodings automatically. That adds complexity and should be deferred until there is a clear requirement.

- Gate file selection and saving to `.txt` paths.
  - Rationale: The initial product scope is explicitly `.txt` files, so file dialogs and validation should reinforce that boundary.
  - Alternative considered: Allow any text-like extension. That expands the behavior contract before the initial app is stable.

## Risks / Trade-offs

- Qt dependency size may be larger than expected -> Keep dependencies minimal and document the Windows environment setup clearly.
- Some existing `.txt` files may use non-UTF-8 encodings -> Show a clear error instead of corrupting content; add encoding support later if needed.
- GUI tests can be brittle in headless environments -> Unit-test file services first and limit GUI verification to import or launch smoke checks.
- Unsaved-change prompts can complicate window state -> Implement a simple dirty-state flag before adding multi-document features.

## Migration Plan

1. Add project metadata, source package, tests, and documentation in the new empty repository.
2. Verify dependency installation and launch command from a clean virtual environment.
3. Rollback is removing the generated scaffold files because there is no existing application state to migrate.

## Open Questions

- None for the initial scaffold. If implementation reveals a Windows-specific Qt issue, document it in the README and adjust verification commands.
