## ADDED Requirements

### Requirement: Python 3.6 Runtime Compatibility
The system SHALL support installation and runtime on Python 3.6 or newer.

#### Scenario: Install on Python 3.6
- **WHEN** the package is installed on Python 3.6
- **THEN** dependency markers select Python 3.6-compatible Qt, SciPy, pytest, and dataclasses packages

#### Scenario: Import UI on old Qt binding
- **WHEN** the application runs with PySide2 instead of PySide6
- **THEN** the UI imports compatible Qt classes and enum constants without failing

### Requirement: Generated Text Splitting Primary Workflow
The system SHALL present TXT-to-generated-text-file splitting as the primary visible application workflow.

#### Scenario: Launch generated text splitting UI
- **WHEN** the user launches the application
- **THEN** the UI shows controls for selecting TXT sources, selecting a destination folder, configuring the size distribution, and generating text files

## REMOVED Requirements

### Requirement: New Text Document
**Reason**: The application is no longer a text editor.
**Migration**: Use source TXT selection and destination generation instead.

### Requirement: Open Text Document
**Reason**: The application is no longer a text viewer/editor.
**Migration**: Select TXT files as generation sources rather than opening them for editing.

### Requirement: Edit And Save Text Document
**Reason**: Manual editing is not part of the generated-text splitting workflow.
**Migration**: Generate output text chunk files into the selected destination folder.

### Requirement: Txt File Boundary
**Reason**: The old open/save boundary is replaced by source-selection and destination-output rules.
**Migration**: Only `.txt` files are accepted as sources and generated outputs are `.txt` files.

### Requirement: Unsaved Change Protection
**Reason**: The application no longer maintains an editable document with unsaved state.
**Migration**: Source files are preserved and generated files are written to a destination folder.
