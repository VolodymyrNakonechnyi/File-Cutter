## ADDED Requirements

### Requirement: Ukrainian File Operations Interface
The system SHALL present the main application UI in Ukrainian and focus the visible workflow on file operations such as reducing `.txt` file sizes.

#### Scenario: Show Ukrainian file-only interface
- **WHEN** the user launches the application
- **THEN** the system displays Ukrainian labels, buttons, prompts, and status messages for selecting a folder, entering a target size, and reducing files

### Requirement: File Or Folder Selection
The system SHALL allow the user to select either one `.txt` file or one folder as the reduction target.

#### Scenario: Reduce one selected txt file
- **WHEN** the user selects a single `.txt` file larger than the target size and starts reduction
- **THEN** the system overwrites that file with valid UTF-8 text no larger than the selected target size

### Requirement: Folder Batch Size Reduction
The system SHALL allow the user to select a folder and reduce supported `.txt` files in that folder to a user-selected target size.

#### Scenario: Reduce oversized txt files in selected folder
- **WHEN** the user selects a folder containing `.txt` files larger than the target size and starts batch reduction
- **THEN** the system overwrites each oversized `.txt` file with valid UTF-8 text no larger than the selected target size

### Requirement: Target Size Input
The system SHALL require a positive integer target size before running file reduction and SHALL support `B`, `KB`, and `MB` size units.

#### Scenario: Reject invalid target size
- **WHEN** the user enters a missing, zero, negative, or non-integer target size
- **THEN** the system prevents reduction and informs the user that a positive integer value is required

#### Scenario: Use non-KB unit
- **WHEN** the user selects `B` or `MB` as the size unit and starts reduction
- **THEN** the system applies the selected unit when calculating the target byte size

### Requirement: Numeric Only Size Entry
The system SHALL constrain the size input control so the user can enter only numeric data for the target size.

#### Scenario: Prevent text in size field
- **WHEN** the user focuses the target size control
- **THEN** the system provides a numeric input that does not accept free-form text such as letters or unit suffixes

### Requirement: Batch Scope Boundary
The system SHALL process only top-level `.txt` files in the selected folder and SHALL NOT process unsupported files or files in subfolders.

#### Scenario: Skip unsupported files and subfolders
- **WHEN** the selected folder contains non-`.txt` files or nested subfolders
- **THEN** the system skips those entries and includes them in the batch results summary as skipped

### Requirement: Preserve Smaller Files
The system SHALL leave `.txt` files unchanged when they are already at or below the selected target size.

#### Scenario: Skip txt file already under target
- **WHEN** a `.txt` file in the selected folder is smaller than or equal to the target size
- **THEN** the system does not rewrite that file and reports it as skipped because it is already within the target

#### Scenario: Keep smaller selected file unchanged
- **WHEN** the user selects a single `.txt` file that is smaller than or equal to the target size
- **THEN** the system does not rewrite that file and reports it as skipped because it is already within the target

### Requirement: Optional Random Fill For Smaller Files
The system SHALL provide an opt-in control that fills `.txt` files smaller than the target size with language-like randomized valid text until they reach the target size.

#### Scenario: Fill smaller files when option enabled
- **WHEN** the user enables randomized fill and processes a `.txt` file smaller than the target size
- **THEN** the system appends randomized valid text that resembles sentence-like language until the file reaches the target size and reports the file as filled

#### Scenario: Leave smaller files unchanged by default
- **WHEN** the user does not enable randomized fill and processes a `.txt` file smaller than the target size
- **THEN** the system leaves the file unchanged and reports it as skipped

### Requirement: Tiny Built-In Text Model
The system SHALL generate language-like filler text using a very small built-in model without requiring external ML dependencies or model downloads.

#### Scenario: Generate filler without large dependency
- **WHEN** the user enables randomized fill
- **THEN** the system generates filler text locally using the built-in tiny character model

### Requirement: Destructive Batch Confirmation
The system SHALL warn the user before running batch reduction because matching files may be overwritten.

#### Scenario: Confirm before reducing folder files
- **WHEN** the user starts batch reduction with a valid folder and target size
- **THEN** the system asks the user to confirm before modifying any files

### Requirement: Batch Results Summary
The system SHALL report the outcome of batch reduction in a compact completion message, including processed files, skipped files, and failures.

#### Scenario: Show batch completion results
- **WHEN** batch reduction finishes
- **THEN** the system displays a compact summary with counts for reduced files, filled files, skipped files, and failed files without listing every processed file

### Requirement: Prominent Processing Action
The system SHALL make the action that starts file processing visually prominent and clearly labeled.

#### Scenario: Identify start processing action
- **WHEN** the user selects a target and target size
- **THEN** the system displays a prominent `ЗАПУСТИТИ ОБРОБКУ` button for starting the operation

### Requirement: Processing Progress Display
The system SHALL show progress while reducing or filling files.

#### Scenario: Show per-file progress
- **WHEN** the system processes multiple `.txt` files
- **THEN** the UI updates a progress bar as each file finishes processing

### Requirement: Batch File Error Handling
The system SHALL continue processing remaining files when one file cannot be read or written.

#### Scenario: Continue after individual file failure
- **WHEN** one `.txt` file in the selected folder fails during batch reduction
- **THEN** the system records that file as failed and continues processing the remaining supported files

### Requirement: Mock Files For Manual Testing
The system SHALL provide a way to generate many mock `.txt` files for manual reduction testing, including files around 100 KB and 200 KB.

#### Scenario: Generate mock test files
- **WHEN** a developer runs the documented mock-file generation command
- **THEN** the system creates a folder of mock `.txt` files with many 100 KB and 200 KB examples for testing reduction behavior

## REMOVED Requirements

### Requirement: New Text Document
**Reason**: The application is now a file-operations utility rather than a text editor.
**Migration**: Use the folder batch reduction workflow to modify supported `.txt` files.

### Requirement: Open Text Document
**Reason**: The application is now a file-operations utility rather than a text editor.
**Migration**: Use folder selection to choose files for batch operations.

### Requirement: Edit And Save Text Document
**Reason**: Manual text editing is no longer part of the visible application workflow.
**Migration**: Use batch reduction to overwrite oversized `.txt` files to the selected target size.

### Requirement: Unsaved Change Protection
**Reason**: The visible editor workflow is removed, so there are no in-app unsaved document edits to protect.
**Migration**: Destructive batch operations use an overwrite confirmation before modifying files.
