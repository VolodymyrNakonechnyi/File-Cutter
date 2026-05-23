## ADDED Requirements

### Requirement: TXT Source Selection
The system SHALL allow the user to select one or more `.txt` source files or a folder containing top-level `.txt` source files.

#### Scenario: Select multiple source files
- **WHEN** the user selects multiple `.txt` files as input
- **THEN** the system includes those files in the source text stream

#### Scenario: Select source folder
- **WHEN** the user selects a folder as input
- **THEN** the system includes top-level `.txt` files from that folder and excludes non-`.txt` files

### Requirement: Destination Folder Selection
The system SHALL require a destination folder where generated text chunk files are written.

#### Scenario: Missing destination folder
- **WHEN** the user starts generation without selecting a destination folder
- **THEN** the system prevents generation and tells the user to select a destination folder

### Requirement: Normal Chunk Size Distribution
The system SHALL sample each output chunk size from a normal distribution configured only by mean KB and standard deviation KB.

#### Scenario: Sample positive chunk size
- **WHEN** the system samples an output chunk size
- **THEN** the sampled size is positive after conversion to bytes

#### Scenario: Resample non-positive size
- **WHEN** the system samples a chunk size that is `<= 0 KB`
- **THEN** the system discards that sample and samples again

#### Scenario: Use default generated text distribution
- **WHEN** the user uses default settings
- **THEN** the system uses generated-text-size distribution defaults with mean `2.5 KB` and standard deviation `1 KB`

### Requirement: SciPy Distribution Engine
The system SHALL use SciPy's normal distribution support to generate output chunk sizes.

#### Scenario: Generate sizes with SciPy norm
- **WHEN** chunk sizes are generated
- **THEN** the system uses `scipy.stats.norm` with the configured mean and standard deviation

### Requirement: UTF-8 Safe Text Slicing
The system SHALL slice source TXT content into output chunks without writing invalid UTF-8.

#### Scenario: Avoid splitting multibyte character
- **WHEN** a sampled byte boundary falls inside a multibyte UTF-8 character
- **THEN** the system adjusts the chunk boundary so the output file remains valid UTF-8

### Requirement: Consume Source Text Into Generated Text Files
The system SHALL write generated text files by consuming source text sequentially until all source TXT content is exhausted.

#### Scenario: Generate text files until input exhausted
- **WHEN** generation starts with valid source files and distribution settings
- **THEN** the system writes sequential `generated_text_XXXXXX.txt` files to the destination folder until all source text has been consumed

### Requirement: Source Preservation
The system SHALL NOT modify selected source files while generating text files.

#### Scenario: Preserve input files
- **WHEN** generation completes
- **THEN** the content and sizes of selected source files remain unchanged

### Requirement: Generation Preview
The system SHALL show a preview of selected source size, distribution settings, and estimated output file count before generation.

#### Scenario: Show estimate before generation
- **WHEN** valid sources and distribution settings are selected
- **THEN** the UI displays total input size and an estimated number of generated text files based on mean chunk size

### Requirement: Generation Progress
The system SHALL show progress while writing generated text files.

#### Scenario: Update progress while writing chunks
- **WHEN** generated text files are being generated
- **THEN** the UI updates progress based on consumed source bytes or generated output files

### Requirement: Compact Completion Summary
The system SHALL show a compact summary after generation completes.

#### Scenario: Show generation summary
- **WHEN** generation finishes
- **THEN** the system displays generated file count, total output bytes, and destination folder without listing every output file

### Requirement: Generated Size Distribution Diagram
The system SHALL generate a visual and textual distribution summary of generated text file sizes after generation completes.

#### Scenario: Write histogram from generated text files
- **WHEN** generated text file generation completes with one or more output files
- **THEN** the system writes an SVG histogram of generated text file sizes to the destination folder

#### Scenario: Show generated size statistics
- **WHEN** the completion summary is shown
- **THEN** the system includes the histogram path, file count, minimum size, median size, mean size, maximum size, and a text histogram of generated text file sizes
