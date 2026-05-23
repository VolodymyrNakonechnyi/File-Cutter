## Why

The current app has drifted around file resizing, random filling, and tiny generated text, but the actual product goal is different: load TXT content and split it into generated text output files whose sizes follow a normal distribution. This change rewrites the app around deterministic text slicing into a destination folder instead of modifying source files in place.

## What Changes

- **BREAKING** Replace the current file reduction/fill workflow with a TXT-to-generated-text-file splitting workflow.
- Add source selection for multiple `.txt` files or a folder of `.txt` files.
- Add destination folder selection where generated `generated_text_XXXXXX.txt` files are written.
- Add SciPy dependency and use `scipy.stats.norm` to sample output chunk sizes from configurable mean and standard deviation values.
- Reject non-positive sampled chunk sizes and resample until the target size is positive.
- Stream input TXT files and slice their existing text into output files; do not generate new text with a neural/filler model.
- Show a preview of distribution settings and progress while files are written.
- Preserve source files unchanged.

## Capabilities

### New Capabilities
- `generated-text-splitting`: Defines loading TXT input, sampling output chunk sizes from a normal distribution, and writing generated text chunks to a destination folder.

### Modified Capabilities
- `txt-file-workspace`: Replace the previous editor/reduction workflow with the generated-text splitting workflow as the primary visible application behavior.

## Impact

- Adds SciPy as a runtime dependency for normal-distribution sampling.
- Replaces most current main-window controls and file-processing service behavior.
- Adds new streaming text slicing and output-writing services.
- Requires tests for distribution sampling, UTF-8-safe slicing, source preservation, destination output naming, and progress reporting.
