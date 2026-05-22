## ADDED Requirements

### Requirement: Runnable Windows Python Qt Application
The system SHALL provide a Windows Python Qt desktop application that can be launched from the project after dependencies are installed.

#### Scenario: Launch application window on Windows
- **WHEN** a developer runs the documented launch command on Windows
- **THEN** the system displays the main desktop application window without requiring additional manual setup

### Requirement: Project Setup Documentation
The system SHALL include project metadata and developer documentation that explain how to install dependencies, run the application, and run verification checks on Windows.

#### Scenario: Fresh checkout setup on Windows
- **WHEN** a developer follows the documented Windows setup steps from a fresh checkout
- **THEN** the application dependencies install successfully and the documented run command is available

### Requirement: New Text Document
The system SHALL allow the user to start a new empty `.txt` document in the application.

#### Scenario: Create empty document
- **WHEN** the user selects the new document action
- **THEN** the editor displays an empty document ready for text input

### Requirement: Open Text Document
The system SHALL allow the user to open an existing `.txt` file and view its text content in the editor.

#### Scenario: Open existing txt file
- **WHEN** the user selects an existing `.txt` file through the open action
- **THEN** the editor displays the file contents and tracks the opened file path as the active document

### Requirement: Edit And Save Text Document
The system SHALL allow the user to edit text and save the active document as a `.txt` file.

#### Scenario: Save existing txt file
- **WHEN** the user edits an opened `.txt` file and selects save
- **THEN** the system writes the editor contents to the active file path

#### Scenario: Save new txt file
- **WHEN** the user edits a new document and selects save
- **THEN** the system prompts for a `.txt` destination and writes the editor contents to that path

### Requirement: Txt File Boundary
The system SHALL restrict the initial open and save workflow to files with a `.txt` extension.

#### Scenario: Reject unsupported file extension
- **WHEN** the user attempts to open or save a file path without the `.txt` extension
- **THEN** the system prevents the operation and informs the user that only `.txt` files are supported

### Requirement: Unsaved Change Protection
The system SHALL warn the user before replacing or closing a document that has unsaved edits.

#### Scenario: Prompt before losing edits
- **WHEN** the active document has unsaved edits and the user starts an action that would discard them
- **THEN** the system prompts the user to save, discard, or cancel before continuing
