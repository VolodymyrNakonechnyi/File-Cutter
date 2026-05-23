## Context

The current application is a Ukrainian TXT file utility that can reduce or fill files. The clarified product goal is to stop modifying source files and instead transform a large body of input TXT content into many generated text output files. Each output file is a chunk of the original input text, and each chunk size is sampled from a normal distribution.

The user explicitly wants normal distribution to shape the output file sizes, not to estimate a separate output count. The system should keep sampling chunk sizes and slicing the source text until all input text is consumed.

## Goals / Non-Goals

**Goals:**
- Support Python 3.6+ installation and runtime.
- Select many TXT inputs by file selection or folder selection.
- Select a destination folder for generated output files.
- Use SciPy `scipy.stats.norm` for normal sampling of output chunk sizes.
- Slice existing input text into output files named predictably, preserving UTF-8 validity.
- Let users configure mean/std in KB with defaults suitable for short generated text files.
- Preserve source files unchanged.
- Show progress and a compact completion summary.

**Non-Goals:**
- Generate new poetic text with neural/filler models.
- Semantically rewrite the source text.
- Process non-`.txt` input files or nested folders in the first version.
- Keep the old resize/fill workflow as a visible primary action.

## Decisions

- Use SciPy `norm` for chunk size sampling.
  - Rationale: The user requested only a mean and standard deviation. Plain normal sampling matches that model directly.
  - Alternative considered: Bounded truncated normal sampling. That adds min/max controls the customer does not want.

- Reject sampled chunk sizes that are `<= 0 KB` and resample.
  - Rationale: File sizes cannot be negative or empty, and rejection preserves the simple mean/std-only UI.
  - Alternative considered: Clamp to 1 byte. That would create artificial spikes of tiny files.

- Interpret distribution settings in KB and convert sampled sizes to bytes with `1 KB = 1024 bytes`.
  - Rationale: The existing app already uses binary KB semantics, and output files are written by byte size.
  - Alternative considered: Decimal KB. That would diverge from the existing implementation and typical filesystem size handling in code.

- Default to a generated-text-size distribution profile: mean `2.5 KB`, std `1 KB`.
  - Rationale: These keep generated chunks short while allowing users to adjust the actual center and spread.

- Slice a UTF-8 byte stream without splitting characters.
  - Rationale: Output files must remain valid TXT. Chunk sizes can be slightly smaller than sampled bytes when a multibyte character crosses the boundary.
  - Alternative considered: Character-count slicing. That ignores the distribution over byte size.

- Write outputs into destination folder as `generated_text_000001.txt`, `generated_text_000002.txt`, etc.
  - Rationale: Predictable names make the result easy to inspect and test.
  - Alternative considered: Use source file names in output names. That becomes confusing when chunks cross input-file boundaries.

- Preserve source files and overwrite only generated output paths when the destination already contains matching output files after confirmation.
  - Rationale: The new workflow is a transformation into a destination folder, not an in-place modifier.
  - Alternative considered: Always fail if destination is non-empty. Safer but annoying during iterative testing.

## Risks / Trade-offs

- Very large inputs can create huge numbers of small output files -> Show a preview and progress; consider batch subfolders if file counts become too large in follow-up work.
- Chunking by byte size can split sentences or stanzas -> This is acceptable because the requirement is size-distributed slicing, not semantic text generation.
- SciPy adds a heavier dependency than the current app -> Keep it as the only new numeric dependency and use it only in the distribution service.
- Plain normal sampling can produce non-positive sizes -> Resample until a positive size is produced.
- Python 3.6 cannot use current PySide6, SciPy, pytest, or PEP 621 packaging -> Use `setup.cfg` metadata, version-specific dependency markers, and PySide2 fallback imports for old interpreters.

## Migration Plan

1. Add SciPy dependency and distribution sampling service.
2. Replace current reduction/fill services with source scanning, UTF-8 streaming/slicing, and destination output writing.
3. Replace the main UI with source selection, destination selection, distribution settings, preview, progress, and generation action.
4. Update README and tests for the new generated-text splitting workflow.
5. Remove or stop exposing old resize/fill controls.

## Open Questions

- Whether output subfolder batching is needed immediately for very large inputs, or only after measuring actual usage.
