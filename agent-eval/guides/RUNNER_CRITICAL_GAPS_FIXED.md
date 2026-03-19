# Runner Critical Gaps - Fixed (Final + Consistency)

## Summary

Fixed all critical and medium gaps in `runner.py` identified in the gap analysis, plus all remaining pre-merge issues and final consistency fixes.

## Critical Gaps Fixed

### 1. Step Order Corrected ✅

**Problem**: HTML report generation was happening BEFORE output writing, but report generation requires `trace_eval.json` which is only written in `_write_outputs()`.

**Fix**:
- Moved Step 9 (output writing) BEFORE Step 10 (report generation)
- Report now correctly reads from freshly written `trace_eval.json`
- Added `_update_results_with_report()` method to update `results.json` after report generation
- Updated module docstring to reflect correct order

**New Flow**:
```
Step 9: Write outputs (trace_eval.json, results.json with report_path=None)
Step 10: Generate HTML report (reads trace_eval.json)
Step 10.1: Update results.json with report path and status
```

### 2. sanitize_filename() Signature Fixed ✅

**Problem**: Runner called `_sanitize(text, max_length)` but report_builder's `sanitize_filename()` only accepts one parameter.

**Fix**:
- Updated runner's `sanitize_filename()` wrapper to call `_sanitize(text)` without max_length
- Applied max_length truncation in the wrapper after calling base sanitizer
- Added edge case handling for max_length < 1
- Strip trailing dots/underscores after truncation to prevent edge cases
- Updated comment to explain the delegation pattern

**After**:
```python
if max_length < 1:
    return "run"

sanitized = _sanitize(text)
sanitized = sanitized[:max_length].strip("._")

return sanitized or "run"
```

### 3. Docstring Updated ✅

**Problem**: Module docstring said "Adapter integration (if needed)" but runner only accepts pre-normalized input.

**Fix**:
- Removed "Adapter integration" from step list
- Added NOTE clarifying adapter integration must happen in CLI/pipeline layer
- Updated step numbers to reflect correct order

### 4. Functional Design Improved ✅

**Problem**: Report couldn't include final results.json data because it was generated before outputs were written.

**Fix**:
- Report now generates AFTER all outputs are written
- `_update_results_with_report()` updates results.json with report path and status
- Report can now read complete results.json with all metadata

### 5. Stale Artifact Bug Prevented ✅

**Problem**: If `trace_eval.json` existed from a previous run, report generation could succeed using old data.

**Fix**:
- Output writing (Step 9) now always happens first, ensuring fresh `trace_eval.json`
- Report generation (Step 10) always reads freshly written artifacts
- No possibility of reading stale data

## Medium Gaps Fixed

### 6. Comment Updated ✅

**Problem**: Comment said "duplicated for backwards compatibility" but function now delegates.

**Fix**:
- Updated comment to say "delegates to report_builder.sanitize_filename for consistency"
- Explained the signature difference and truncation handling

### 7. Dead State Removed ✅

**Problem**: `self._worker_pool = None` was initialized but never used (worker pool not cached).

**Fix**:
- Removed `self._worker_pool = None` from `__init__`
- `_get_worker_pool()` explicitly doesn't cache, so field is unnecessary

### 8. Unused Import Removed ✅

**Problem**: `re` module imported but not used (sanitization delegated to report_builder).

**Fix**:
- Removed `import re` from imports

## Pre-Merge Issues Fixed

### 9. sanitize_filename() Edge Case Fixed ✅

**Problem**: Function could return empty string if max_length == 0, violating contract.

**Fix**:
```python
if max_length < 1:
    return "run"

sanitized = _sanitize(text)
sanitized = sanitized[:max_length].strip("._")

return sanitized or "run"
```

### 10. Stale Checksum Metadata Fixed ✅

**Problem**: `_update_results_with_report()` modified results.json but didn't update `artifact_hashes`, causing stale metadata.

**Fix**:
- `_update_results_with_report()` now recomputes all artifact_hashes after modification
- Uses output_writer.compute_file_hash() for consistency
- Maintains integrity of artifact_hashes field

### 11. Atomic Write Pattern Added ✅

**Problem**: `_update_results_with_report()` wrote directly to results.json without atomic pattern.

**Fix**:
- Implemented temp file + replace pattern
- Writes to `results.json.tmp` first
- Uses `temp_path.replace(results_path)` for atomic operation
- Matches safety pattern used in report writing

### 12. execution_stats Mutation Prevented ✅

**Problem**: `_write_outputs()` mutated caller's execution_stats dict.

**Fix**:
```python
execution_stats_for_output = dict(execution_stats)
execution_stats_for_output["report_generation_status"] = report_generation_status
```
- Creates copy before modification
- Passes copy to write_results_json
- Original dict remains unchanged

### 13. All FIX Comments Removed ✅

**Problem**: Code contained temporary FIX comments from development.

**Fix**:
- Removed all "FIX" comments
- Kept explanatory comments where needed
- Clean, production-ready code

## Verification

All changes verified with:
- No syntax errors (getDiagnostics passed)
- Correct step order in run() method
- Proper signature for sanitize_filename wrapper with edge case handling
- Updated docstrings and comments
- Clean imports
- Atomic write pattern for results.json updates
- No dict mutation side effects
- Checksum integrity maintained

## Impact

These fixes ensure:
1. Report generation always has access to complete, fresh canonical artifacts
2. No signature mismatches or TypeErrors
3. No stale artifact bugs
4. No stale checksum metadata
5. Atomic file operations for safety
6. No side effects from dict mutations
7. Clear, accurate documentation
8. Clean, maintainable, production-ready code

## Files Modified

- `agent-eval/agent_eval/evaluators/trace_eval/runner.py`

## Final Consistency Fixes (Latest)

### 14. Module Docstring Step Numbering Fixed ✅

**Problem**: Module docstring listed 9 steps but implementation had 10+ steps, and step descriptions didn't match implementation.

**Fix**:
- Updated module docstring to list all 11 steps explicitly:
  1. Load input (NormalizedRun JSON)
  2. Validate input against schema
  3. Compute deterministic metrics
  4. Load and merge rubrics
  5. Load judge configuration
  6. Build judge clients
  7. Build JudgeJob queue
  8. Execute jobs via worker pool
  9. Aggregate results (within-judge and cross-judge)
  10. Write output files (trace_eval.json, results.json)
  11. Generate HTML report (requires outputs from step 10)

### 15. Implementation Step Numbering Fixed ✅

**Problem**: Step numbering in run() method was inconsistent (had Step 5.5, duplicate Step 7, etc.)

**Fix**:
- Updated all step numbers in run() method to match module docstring (1-11)
- Removed "Step 5.5" and renumbered subsequent steps
- Fixed duplicate "Step 7" issue
- All steps now consistently numbered from 1 to 11

### 16. __init__ Docstring Step Reference Fixed ✅

**Problem**: `skip_report` parameter said "Step 9" but report generation is now Step 11.

**Fix**:
- Updated `skip_report` docstring to say "Step 11"

### 17. artifact_hashes vs artifact_checksums Consistency ✅

**Problem**: Runner used `artifact_hashes` but report_builder expects `artifact_checksums`, causing potential mismatch.

**Fix**:
- Updated `_update_results_with_report()` to handle both keys for backward compatibility
- Checks for `artifact_checksums` first (new standard), falls back to `artifact_hashes` (legacy)
- Initializes `artifact_checksums` if neither key exists (no more silent skip)
- Updated docstring to clarify it uses artifact_checksums key to match report_builder expectations
- This ensures runner works with both old and new output_writer versions

**Code**:
```python
# Handle both artifact_checksums (new) and artifact_hashes (legacy) for backward compatibility
checksum_key = "artifact_checksums" if "artifact_checksums" in results else "artifact_hashes"

if checksum_key in results:
    output_writer = self._get_output_writer()
    for artifact_name, artifact_path in results["artifact_paths"].items():
        if artifact_path:
            try:
                results[checksum_key][artifact_name] = output_writer.compute_file_hash(artifact_path)
            except (FileNotFoundError, IOError):
                results[checksum_key][artifact_name] = None
```

### 18. Checksum Initialization When Neither Key Exists ✅

**Problem**: If neither `artifact_checksums` nor `artifact_hashes` existed in results.json, the checksum update was silently skipped entirely.

**Fix**:
- Three-way resolution: prefer `artifact_checksums`, fall back to `artifact_hashes`, initialize `artifact_checksums` if neither exists
- Checksums are always updated, never silently skipped

**Code**:
```python
if "artifact_checksums" in results:
    checksum_key = "artifact_checksums"
elif "artifact_hashes" in results:
    checksum_key = "artifact_hashes"
else:
    checksum_key = "artifact_checksums"
    results[checksum_key] = {}
```

### 19. results.json Self-Checksum Explicitly Excluded ✅

**Problem**: After rewriting results.json, any checksum entry for results.json itself would be stale. It was unclear whether this was intentional.

**Fix**:
- Documented explicitly in docstring that results.json is NOT self-hashed (the write would invalidate the hash)
- Only artifacts listed in `artifact_paths` are checksummed (judge_runs, trace_eval, report)
- Added explicit guard: `if artifact_name == "results": continue` to prevent accidental self-hashing even if artifact_paths evolves

### 20. _update_results_with_report() Returns Success/Failure ✅

**Problem**: Method was `-> None` and too quiet on failure. Report module depends on this metadata, so silent failure could cause downstream issues.

**Fix**:
- Changed return type to `-> bool` (True on success, False on failure)
- Callers in `run()` now check return value and log degraded-state warnings
- Added `self.debug` traceback on failure for diagnosability

### 21. Checksum Key Shape Verified ✅

**Problem**: Concern that `_update_results_with_report()` might create mixed-structure checksums if keys didn't match between `artifact_paths` and the checksum dict.

**Verification**:
- `_write_outputs()` builds `artifact_paths` with logical keys: `judge_runs`, `trace_eval`, `report`
- `write_results_json()` iterates `artifact_paths.items()` to build `artifact_hashes` with the same logical keys
- `_update_results_with_report()` iterates `results["artifact_paths"].items()` — same logical keys
- Shape is consistent across all three sites. No mixed-structure risk.

### 22. AdapterError Annotated as Legacy Dead Code ✅

**Problem**: `AdapterError` class and its `except` branch in `run()` are dead code — this runner explicitly does not do adapter work, nothing raises it, and nothing imports it from runner.

**Fix**:
- Added docstring note explaining it is retained for backward compatibility with CLI/pipeline error handling
- Marked for removal once all callers are confirmed migrated
- Not removed yet to avoid breaking any external `except AdapterError` handlers

### 23. JSONL Read Path Now Specifies UTF-8 Encoding ✅

**Problem**: `_aggregate_results()` opened `judge_runs.jsonl` without explicit encoding, while all other file operations in runner use `encoding='utf-8'`.

**Fix**:
- Changed to `open(judge_runs_path, 'r', encoding='utf-8')`
- Also fixed Step 1 input load to use explicit `encoding='utf-8'`
- All file reads in runner now consistently specify encoding

### 24. Skip-Report Branch Now Checks Update Return Value ✅

**Problem**: The success and failure branches checked `_update_results_with_report()` return value, but the `skip_report` branch ignored it. Inconsistent.

**Fix**:
- Skip branch now checks return value and logs degraded-state warning on failure
- All three call sites are now consistent

### 25. Rubric Helper Functions Promoted to Module Level ✅

**Problem**: `_rubric_id()` and `_rubric_scale()` were recreated as closures on every `_aggregate_results()` call. Not a performance issue, but poor for readability and reuse.

**Fix**:
- Moved both functions to module level (after `sanitize_filename`)
- No closure state needed — they only inspect their argument
- Available for reuse by other modules if needed
- Added return type annotations (`Optional[str]` and `Optional[Any]`)

### 26. Checksum Exception Handling Widened to OSError ✅

**Problem**: `_update_results_with_report()` caught `FileNotFoundError` and `IOError` for checksum failures, but `OSError` (which is the parent of both) also covers permission errors and other OS-level issues that can occur in varied environments.

**Fix**:
- Changed to `except OSError` which covers `FileNotFoundError`, `IOError`, `PermissionError`, and all other OS-level file access errors

### 27. Step 11 Comment Tightened to Specify Actual Dependency ✅

**Problem**: Comment said "requires outputs from step 10" which is vague. The actual dependency is that `trace_eval.json` and `results.json` must exist with the expected schema.

**Fix**:
- Updated module docstring: "reads trace_eval.json and results.json from step 10"
- Updated inline comment: "Depends on trace_eval.json and results.json existing with the expected schema. generate_report() reads these artifacts directly from output_dir."

### 28. Pre-Flight Artifact Check Before Report Generation ✅

**Problem**: No explicit validation that report input artifacts (trace_eval.json, results.json) actually exist before calling generate_report(). Step ordering guarantees this in practice, but a missing artifact would produce a confusing downstream error.

**Fix**:
- Added pre-flight check in `_generate_html_report()` that verifies both `trace_eval.json` and `results.json` exist
- Raises `FileNotFoundError` with a clear message referencing Step 10 if artifacts are missing
- Turns a confusing downstream error into an early, obvious failure

## Architectural Notes (Post-Merge)

These are design observations that are acceptable for merge but should be addressed in follow-up work:

1. **sanitize_filename() depends on reporting layer** — the dependency direction is odd (runner → reporting for a general utility). Should move to a shared utility module.

2. **AdapterError is transitional baggage** — annotated with removal guidance. Track cleanup item to remove once all callers are confirmed migrated.

3. **_update_results_with_report() is runner-owned mutation of writer-owned artifact** — creates split-brain ownership. Long-term, report metadata update logic should live in OutputWriter or a dedicated artifact manager.

4. **Checksum key compatibility is transitional** — supporting both `artifact_checksums` and `artifact_hashes` is practical. Decide one canonical field and treat the other as legacy-read only.

5. **Report metadata persistence failure is non-fatal by design** — evaluation succeeds with incomplete metadata. This is a product decision: incomplete report metadata is considered degraded-but-valid.

6. **report_generation_status can drift from actual state** — if report succeeds but `_update_results_with_report()` fails, logs show success but file may still say "pending". Warnings are emitted, but persisted state can disagree with runtime truth.

7. **run() is doing a lot** — orchestration + degraded-state handling + report lifecycle. Extracting `_handle_report_generation()` would improve maintainability.

8. **execution_stats schema is runner-authored** — fields like `aggregation_stats` and `report_generation_status` are added by runner, not centrally defined. Should be documented in the results.json contract.

9. **Initial results.json contains placeholder report state** — first write says "pending", then post-step patch changes it. Two-phase state is by design; tests should assert it intentionally.

10. **Directory fsync after atomic replace** — current pattern does fsync on temp file content but not on parent directory after replace(). Stronger crash-safety if needed, but overkill for most environments.

11. **Integration tests matter more than comments** — the Step 11 dependency is not just "outputs exist" but that trace_eval.json/results.json shape matches what generate_report() expects. Integration test coverage is the real safety net.

## Testing Recommendations

1. Run full evaluation with report generation enabled
2. Verify report includes data from results.json
3. Verify no stale artifact issues with multiple runs
4. Verify report_path and report_generation_status in results.json
5. Verify artifact checksums are correct after report generation (both artifact_hashes and artifact_checksums keys)
6. Test with --skip-report flag
7. Test edge cases: max_length=0, empty run_id, etc.
8. Verify atomic write behavior (interrupt during write)
9. Verify step numbering consistency in logs
10. Test backward compatibility with both artifact_hashes and artifact_checksums
11. Verify checksum initialization when neither key exists in results.json
12. Verify _update_results_with_report returns False on failure and caller logs degraded state

## Known External Issues

### artifact_hashes vs artifact_checksums in output_writer

**Issue**: output_writer.py currently writes `artifact_hashes` but report_builder.py expects `artifact_checksums`.

**Impact**: Report builder may not find checksums in results.json if output_writer hasn't been updated.

**Mitigation**: Runner now handles both keys for backward compatibility, so it works with either version of output_writer.

**Resolution**: This should be fixed in output_writer.py in a separate PR to standardize on `artifact_checksums`.


## Round 3 Fixes (Fixes 29-32)

### 29. Directory fsync After Atomic Replace ✅

**Problem**: `_update_results_with_report()` did fsync on the temp file content but not on the parent directory after `replace()`. On power failure, the directory entry update could be lost.

**Fix**:
- Added `os.open(str(self.output_dir), os.O_RDONLY)` + `os.fsync(dir_fd)` after `temp_path.replace(results_path)`
- Ensures the rename is durable even on crash
- Wrapped in try/finally to guarantee fd is closed

### 30. Narrowed Exception Handling in _update_results_with_report() ✅

**Problem**: Broad `except Exception` caught both operational failures (file I/O, JSON errors) and programmer bugs (KeyError, TypeError, AttributeError). Programmer bugs were silently downgraded to warnings.

**Fix**:
- Changed to `except (OSError, json.JSONDecodeError, ValueError)` — covers all expected operational failures
- Programmer bugs (KeyError, TypeError, AttributeError) now propagate and surface during development
- Updated docstring to explain the intentional narrowing

### 31. Tightened _rubric_scale() Return Type ✅

**Problem**: `Optional[Any]` was honest but too loose for maintainability. Callers need to know the return is either a dict or a ScoringScale object.

**Fix**:
- Changed return type to `Optional[Union[Dict[str, Any], "ScoringScale"]]`
- Added docstring explaining both forms and pointing callers to `_aggregate_results` for conversion logic
- `"ScoringScale"` is a forward reference string to avoid import at module level

### 32. Extracted _handle_report_lifecycle() Helper ✅

**Problem**: `run()` was doing orchestration, degraded-state handling, and report metadata persistence all inline. The Step 11 block was ~30 lines of branching logic.

**Fix**:
- Extracted `_handle_report_lifecycle(run_id)` method that encapsulates:
  - Generate report (or skip if configured)
  - Persist report path and status to results.json
  - Emit degraded-state warnings if metadata persistence fails
- `run()` Step 11 is now a single line: `report_path, report_generation_status = self._handle_report_lifecycle(run_id)`
- Easier to test report lifecycle in isolation

## Updated Architectural Notes (Post-Merge)

Items resolved by Round 3 fixes:
- ~~Directory fsync~~ → Fixed (#29)
- ~~Broad exception catch~~ → Fixed (#30)
- ~~_rubric_scale() typing~~ → Fixed (#31)
- ~~run() too large~~ → Partially addressed (#32, report lifecycle extracted)

Remaining architectural items:
1. **sanitize_filename() depends on reporting layer** — inverted dependency, should move to shared utility
2. **AdapterError is dead in this runner** — well-documented, still cleanup debt
3. **results.json post-write mutation** — runner patches writer-owned artifact, split-brain ownership
4. **Checksum key compatibility is transitional** — pick one canonical field eventually
5. **State can drift if report succeeds but metadata update fails** — degraded-but-valid by design
6. **No schema validation of report input artifacts** — existence checked, content/schema not validated
7. **execution_stats schema is runner-authored** — not centrally defined


## Round 4 Fixes (Fixes 33-37)

### 33. sanitize_filename() Moved to Shared Utility Module ✅

**Problem**: Runner imported `sanitize_filename` from `reporting.report_builder`, creating an inverted dependency (orchestrator depending on reporting layer for a general-purpose utility). Pipeline had its own duplicate copy.

**Fix**:
- Created `agent_eval/evaluators/trace_eval/filename_utils.py` as the canonical implementation
- Runner, report_builder, and pipeline all delegate to `filename_utils.sanitize_filename`
- Removed duplicate regex logic from all three modules
- Removed unused `import re` from report_builder.py and pipeline.py
- Backward-compatible: existing imports from report_builder and pipeline still work

### 34. _rubric_scale() Type Annotation Made Honest ✅

**Problem**: Previous fix typed return as `Optional[Union[Dict, "ScoringScale"]]`, but the implementation can also return arbitrary objects with `.type/.min/.max/.values` attributes. The type hint was optimistic.

**Fix**:
- Reverted to `Optional[Any]` with an expanded docstring explaining the three possible return forms (dict, ScoringScale, arbitrary attribute-bearing object)
- The docstring now explicitly states this is honest, not loose — the rubric source is not constrained to a single schema

### 35. _handle_report_lifecycle() Exception Handling Narrowed ✅

**Problem**: Broad `except Exception` caught both report-layer errors and programmer bugs, downgrading all to warnings.

**Fix**:
- First catches `(FileNotFoundError, OSError)` for pre-flight and file system errors
- Second catches `Exception` but distinguishes `ReportGenerationError` (expected report failure) from unexpected errors (possible bugs)
- Unexpected errors get a distinct warning message: "may be a bug"
- `generate_report()` wraps all internal errors into `ReportGenerationError`, so true programmer bugs in runner code around the call will surface with the "may be a bug" label

### 36. Lazy-Loader Helper Methods Now Typed ✅

**Problem**: `_get_validator()`, `_get_rubric_loader()`, `_get_judge_config_loader()`, `_get_deterministic_metrics()`, `_get_job_builder()`, `_get_worker_pool()`, `_get_aggregator()`, `_get_output_writer()` all had no return type annotations.

**Fix**:
- Added `TYPE_CHECKING` imports for all lazy-loaded types
- Added return type annotations using string forward references
- `_handle_report_lifecycle()` return typed as `Tuple[Optional[str], str]`

### 37. Unused `import re` Removed from report_builder.py and pipeline.py ✅

**Problem**: After delegating `sanitize_filename` to the shared utility, `re` was no longer used in either module.

**Fix**:
- Removed `import re` from both files

## Updated Architectural Notes (Post-Merge)

Items resolved by Round 4 fixes:
- ~~sanitize_filename() depends on reporting layer~~ → Fixed (#33, moved to shared utility)
- ~~Loose helper typing~~ → Fixed (#36, all lazy-loaders typed)
- ~~_handle_report_lifecycle() broad-catches Exception~~ → Fixed (#35, narrowed with bug detection)
- ~~_rubric_scale() type optimistic~~ → Fixed (#34, honest Optional[Any] with documented rationale)

Remaining architectural items:
1. **AdapterError is dead in this runner** — well-documented, still cleanup debt
2. **results.json post-write mutation** — runner patches writer-owned artifact, split-brain ownership
3. **Checksum key compatibility is transitional** — pick one canonical field eventually
4. **State can drift if report succeeds but metadata update fails** — degraded-but-valid by design
5. **No schema/content validation of report input artifacts** — existence checked, content/schema not validated
6. **_update_results_with_report() can set checksum entries to None** — hides missing artifacts unless downstream validates
7. **execution_stats schema is runner-authored** — not centrally defined


## Round 5 Fixes (Fixes 38-39) — filename_utils.py

### 38. Defensive Type Coercion for Non-String Input ✅

**Problem**: If a caller accidentally passed `None` or a non-string value, `re.sub` would raise `TypeError` inside the utility. Fail-fast is one option, but since this is a shared utility used across layers, defensive coercion is safer.

**Fix**:
- `None` returns `"run"` immediately (most common accidental case)
- Non-string values are coerced via `str()` before sanitization
- Documented in docstring and module-level design decisions

### 39. Windows Reserved Name Handling ✅

**Problem**: Names like `CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`, `LPT1`-`LPT9` are reserved on Windows and cannot be used as filenames. If this utility is ever used in a cross-platform context, these would cause failures.

**Fix**:
- Added `_WINDOWS_RESERVED` frozenset with all reserved device names
- After sanitization, checks if result matches a reserved name (case-insensitive)
- Prefixes with `_` if reserved (e.g., `CON` → `_CON`)
- Re-truncates after prefix to respect max_length
- Documented in module-level design decisions

### Architectural Notes for filename_utils.py

These are design observations, not bugs:

1. **Multiple underscores are preserved** — `test/run/../001` → `test_run___001`. This is intentional: collapsing underscores would change positional semantics and break existing test expectations.

2. **No extension-aware truncation** — truncation may cut through a `.json` extension. This is acceptable because this utility is for run IDs and identifiers, not user-facing filenames with meaningful extensions.

3. **All three consumers now delegate here** — runner.py, report_builder.py, and pipeline.py all import from `filename_utils`. No duplicate regex logic remains.


## Round 6 Fixes (Fixes 40-48) — Pipeline + Runner Ownership

### 40. Removed Duplicate Normalized Artifact Write from Runner ✅

**Problem**: Both pipeline and runner wrote `normalized_run.{safe_run_id}.json`. Pipeline's docstring claimed to be the single source of truth for normalized artifact persistence, but runner was also doing it.

**Fix**:
- Removed the normalized artifact write from runner's `run()` method (between Step 2 and Step 3)
- Added comment: "Normalized artifact persistence is owned by the pipeline layer"
- Pipeline remains the sole writer of normalized artifacts

### 41. Removed Local sanitize_filename Wrapper from Pipeline ✅

**Problem**: Pipeline had a local wrapper function for backward compatibility, but no external callers import `sanitize_filename` from pipeline.

**Fix**:
- Replaced wrapper with direct import: `from agent_eval.evaluators.trace_eval.filename_utils import sanitize_filename`
- Removed the wrapper function entirely

### 42. detect_input_format() Now Raises on Malformed JSON ✅

**Problem**: Invalid JSON was silently treated as "raw" format, hiding broken input files and deferring failure into adapter code where the error message would be confusing.

**Fix**:
- `json.JSONDecodeError` now raises `PipelineError` with a clear message identifying the file and parse error
- Schema-invalid but valid JSON is still correctly treated as "raw"

### 43. All File Reads Now Specify encoding='utf-8' ✅

**Problem**: Several `open()` calls in pipeline used default encoding instead of explicit `encoding='utf-8'`.

**Fix**:
- Updated all file reads in `detect_input_format()` and `run_pipeline()` to use `encoding='utf-8'`

### 44. Timestamp-Based run_id Fallback Instead of "unknown" ✅

**Problem**: Using `"unknown"` as fallback run_id could cause artifact collisions if multiple files are processed without run_id.

**Fix**:
- Changed fallback to `f"run_{int(time.time() * 1000)}"` — same pattern runner uses
- Collision-safe: millisecond timestamp ensures uniqueness

### 45. Pipeline Now Passes skip_report and enable_charts to TraceEvaluator ✅

**Problem**: Runner supports `skip_report` and `enable_charts`, but pipeline didn't expose or pass them, making pipeline a narrower interface than runner.

**Fix**:
- Added `skip_report: bool = False` and `enable_charts: bool = True` parameters to `run_pipeline()`
- Both are passed through to `TraceEvaluator` constructor
- CLI updated to pass `skip_report` through to `run_pipeline()`

### 46. Enriched Pipeline Result Payload ✅

**Problem**: Pipeline result only contained basic info. Downstream callers needed run_id and artifact paths.

**Fix**:
- Added `run_id`, `trace_eval_path`, and `results_path` to the result dict
- Artifact paths are only included if the files actually exist (checked via `.exists()`)

### 47. Adapter Exceptions Now Caught Specifically ✅

**Problem**: Adapter failures were wrapped in generic `PipelineError("Pipeline execution failed: ...")`, making it hard to distinguish adapter errors from other pipeline errors.

**Fix**:
- Added `AdapterExecutionError(PipelineError)` exception class
- `adapt()` failures now raise `AdapterExecutionError` with clear message: `"Generic_JSON_Adapter failed on {path}: {error}"`
- Re-raise clause updated to pass through both `PipelineError` and `AdapterExecutionError`

### 48. Pipeline Docstring Updated to Match Implementation ✅

**Problem**: Docstring said "Pipeline is single source of truth for normalized artifact persistence" but runner was also writing normalized artifacts.

**Fix**:
- Runner no longer writes normalized artifacts (Fix #40)
- Pipeline docstring now accurately says: "runner does NOT write normalized artifacts"
- Architecture comment in runner confirms pipeline ownership

### Pipeline Architectural Notes (Post-Merge)

1. **Validation is still done twice in the normalized branch** — `detect_input_format()` validates once, then `run_pipeline()` validates again. Could return validated data from detection, but the redundancy is harmless and provides defense-in-depth.
2. **Adapter output write does not use SafeJSONEncoder** — if adapter ever returns datetime/Decimal objects, plain `json.dump` will fail. Currently adapter returns pure JSON-safe dicts, so this is not a bug yet.


## Round 7 Fixes (Fixes 49-52) — Pipeline Polish

### 49. Simplified Redundant Exception Clause ✅

**Problem**: `except (PipelineError, AdapterExecutionError)` was redundant since `AdapterExecutionError` already subclasses `PipelineError`.

**Fix**:
- Simplified to `except PipelineError:` with comment noting subclass coverage

### 50. Normalized Artifact Write Now Uses SafeJSONEncoder ✅

**Problem**: `json.dump(validated_data, ...)` used the default encoder. If `validator.validate()` ever returns objects containing `datetime`, `Decimal`, or other non-native JSON types, the write would fail.

**Fix**:
- Imported `SafeJSONEncoder` from runner
- Applied `cls=SafeJSONEncoder` to the normalized artifact write
- Matches runner's encoding behavior for consistency

### 51. output_dir Resolved to Absolute Path ✅

**Problem**: `output_dir` in the result dict was the raw input string, which could be relative. Downstream callers may need a resolved absolute path.

**Fix**:
- `output_path = Path(output_dir).resolve()` — resolves to absolute path at pipeline entry
- Result dict uses `str(output_path)` instead of raw `output_dir`
- Verbose summary also uses resolved path

### 52. Verbose Log Wording Fixed ✅

**Problem**: For normalized input, the log said "copying to output directory" but the code actually loads, validates, and writes a canonical artifact. "Copying" was inaccurate.

**Fix**:
- Changed to "validating and persisting to output directory"

### Pipeline Architectural Notes (Post-Merge, Updated)

1. **Double validation for normalized input** — `detect_input_format()` validates once, `run_pipeline()` validates again. Safe but redundant. Could return validated data from detection later.
2. **Adapter exception catch is broad** — wraps all adapter errors as `AdapterExecutionError`, including programmer bugs. Acceptable until adapter exposes a stable error type.
3. **trace_eval_path/results_path may exist on partial failure** — files are reported if they exist regardless of exit code. Callers should check `success` field, not just path presence.
4. **Normalized artifact ownership is now an architectural contract** — runner does not write normalized artifacts. Should be enforced by integration test.


## Round 8 Fixes (Fixes 53-54) — Pipeline Final Polish

### 53. TraceEvaluator Now Receives Resolved output_dir ✅

**Problem**: Pipeline resolved `output_path = Path(output_dir).resolve()` but still passed the raw `output_dir` string to `TraceEvaluator(output_dir=output_dir)`. Pipeline and runner could theoretically disagree on the canonical directory.

**Fix**:
- Changed to `output_dir=str(output_path)` so both pipeline and runner use the same resolved absolute path

### 54. Return Contract Docstring Matches Implementation ✅

**Problem**: Docstring said `trace_eval_path` and `results_path` are returned "if evaluation succeeded", but code returns them whenever the files exist on disk, even on failure.

**Fix**:
- Updated docstring to accurately state: "None if file does not exist"
- Added Note section: callers should check `success` field, not just path presence
