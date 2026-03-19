# Comprehensive System Testing — Evidence Report

Spec: `.kiro/specs/comprehensive-system-testing/`  
Date: March 19, 2026  
Policy: Test-only — zero production source files modified under `agent-eval/agent_eval/`

## Summary

| Scope | Passed | Failed | Notes |
|-------|--------|--------|-------|
| System tests (`tests/system/`) | 280 | 0 | All green |
| Full suite (`tests/`) | 429 | 1 | Pre-existing failure (unrelated) |

The single failure is `test_security_requirements.py::TestJinja2Autoescape::test_autoescape_enabled_in_template_rendering` — a `ReportViewModel` constructor mismatch (`generated_at` kwarg) that predates this spec.

## Test File Inventory (20 files, 280 tests)

| File | Tests | Coverage Area |
|------|-------|---------------|
| test_e2e_pipeline.py | 15 | End-to-end raw/normalized/error/degraded scenarios |
| test_aggregation_filtering.py | 19 | 5-gate JSONL filtering (malformed, missing fields, bad JobResult, run_id mismatch, empty turn_id) |
| test_cli_error_handling.py | 15 | PipelineError propagation, KeyboardInterrupt, unexpected exceptions, --debug traces |
| test_report_lifecycle.py | 13 | Skip/success/failure report paths, results.json update isolation |
| test_pipeline_detection.py | 17 | Input format heuristic, normalized vs raw classification, boundary cases |
| test_cli_validation.py | 6 | Exit codes, severity ordering, path resolution |
| test_cli_entrypoint.py | 22 | Entrypoint convergence, flag acceptance |
| test_pipeline_adapter.py | 9 | Adapter invocation, error propagation |
| test_pipeline_persistence.py | 12 | Normalized artifact write-once, sanitize_filename usage, fallback run_id |
| test_pipeline_payload.py | 26 | Result dict keys, success/exit_code consistency, artifact path validity |
| test_aggregation_structure.py | 12 | Result dict shape, cross_judge_results equality, judge_summary accounting |
| test_aggregation_scoring.py | 9 | Scoring scale variants (dict, dataclass, generic object, None) |
| test_runner_config.py | 9 | Malformed YAML, 0/5 judges, invalid rubrics, duplicate rubric IDs |
| test_output_artifacts.py | 14 | trace_eval.json and results.json content, report_generation_status |
| test_report_preflight.py | 3 | Missing trace_eval.json / results.json pre-flight checks |
| test_atomic_update.py | 19 | Atomic write pattern, operational errors return False, programmer bugs propagate |
| test_checksum_resolution.py | 12 | Checksum key precedence, recomputation, no-self-hash, missing artifact → None |
| test_filename_sanitization.py | 40 | Safe chars, unsafe replacement, empty fallback, truncation, Windows reserved names |
| test_fixtures_smoke.py | 4 | Fixture validity smoke tests |
| conftest.py | — | Shared fixtures and helpers |

---

## Evidence: 5 Key Test Files (Verbose Output)

### 1. End-to-End Pipeline (`test_e2e_pipeline.py`) — 15 passed

Runs the full `run_pipeline()` with real adapter, evaluator, aggregator, and mock judges.

```
test session starts
platform darwin -- Python 3.11.14, pytest-9.0.2

test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_pipeline_succeeds PASSED                 [  6%]
test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_produces_all_artifacts PASSED            [ 13%]
test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_report_generated_when_not_skipped PASSED [ 20%]
test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_result_paths_point_to_existing_files PASSED [ 26%]
test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_pipeline_succeeds PASSED   [ 33%]
test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_produces_same_artifacts_as_raw PASSED [ 40%]
test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_report_generated PASSED    [ 46%]
test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_result_paths_valid PASSED  [ 53%]
test_e2e_pipeline.py::TestE2EErrorScenarios::test_adapter_failure_raises_with_exit_code_1 PASSED      [ 60%]
test_e2e_pipeline.py::TestE2EErrorScenarios::test_report_failure_still_returns_success PASSED         [ 66%]
test_e2e_pipeline.py::TestE2EErrorScenarios::test_skip_report_returns_success_no_html PASSED          [ 73%]
test_e2e_pipeline.py::TestE2EDegradedAggregation::test_degraded_aggregation_succeeds_with_partial_results PASSED [ 80%]
test_e2e_pipeline.py::TestE2EArtifactPathReportingOnFailure::test_failure_after_partial_artifacts_reports_existing_paths PASSED [ 86%]
test_e2e_pipeline.py::TestE2EArtifactPathReportingOnFailure::test_failure_reports_none_for_missing_artifacts PASSED [ 93%]
test_e2e_pipeline.py::TestE2EArtifactPathReportingOnFailure::test_failure_existing_artifact_paths_are_accessible PASSED [100%]

15 passed in 3.95s
```

### 2. Aggregation 5-Gate Filtering (`test_aggregation_filtering.py`) — 19 passed

Validates each of the 5 JSONL filtering gates independently.

```
test session starts
platform darwin -- Python 3.11.14, pytest-9.0.2

test_aggregation_filtering.py::TestGate1MalformedJson::test_malformed_json_line_skipped PASSED        [  5%]
test_aggregation_filtering.py::TestGate1MalformedJson::test_multiple_malformed_json_lines PASSED      [ 10%]
test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[job_id] PASSED [ 15%]
test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[rubric_id] PASSED [ 21%]
test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[judge_id] PASSED [ 26%]
test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[status] PASSED [ 31%]
test_aggregation_filtering.py::TestGate3BadJobResult::test_invalid_status_value_skipped PASSED        [ 36%]
test_aggregation_filtering.py::TestGate3BadJobResult::test_missing_timestamp_skipped PASSED           [ 42%]
test_aggregation_filtering.py::TestGate4RunIdMismatch::test_different_run_id_skipped PASSED           [ 47%]
test_aggregation_filtering.py::TestGate4RunIdMismatch::test_matching_run_id_accepted PASSED           [ 52%]
test_aggregation_filtering.py::TestGate4RunIdMismatch::test_empty_run_id_accepted PASSED              [ 57%]
test_aggregation_filtering.py::TestGate4RunIdMismatch::test_none_run_id_accepted PASSED               [ 63%]
test_aggregation_filtering.py::TestGate4RunIdMismatch::test_mixed_run_ids_filters_correctly PASSED    [ 68%]
test_aggregation_filtering.py::TestGate5EmptyTurnIdNormalized::test_empty_turn_id_normalized_to_none PASSED [ 73%]
test_aggregation_filtering.py::TestGate5EmptyTurnIdNormalized::test_non_empty_turn_id_preserved PASSED [ 78%]
test_aggregation_filtering.py::TestNoValidRuns::test_all_lines_malformed_returns_empty PASSED         [ 84%]
test_aggregation_filtering.py::TestNoValidRuns::test_all_lines_wrong_run_id_returns_empty PASSED      [ 89%]
test_aggregation_filtering.py::TestNoValidRuns::test_empty_jsonl_returns_empty PASSED                 [ 94%]
test_aggregation_filtering.py::TestNoValidRuns::test_mixed_failures_all_filtered_returns_empty PASSED [100%]

19 passed in 0.36s
```

### 3. CLI Error Handling (`test_cli_error_handling.py`) — 15 passed

Verifies error propagation, exit codes, and debug stack trace behavior.

```
test session starts
platform darwin -- Python 3.11.14, pytest-9.0.2

test_cli_error_handling.py::TestPipelineErrorPropagation::test_pipeline_error_returns_its_exit_code PASSED       [  6%]
test_cli_error_handling.py::TestPipelineErrorPropagation::test_pipeline_validation_error_returns_exit_code_4 PASSED [ 13%]
test_cli_error_handling.py::TestPipelineErrorPropagation::test_pipeline_config_error_returns_exit_code_3 PASSED  [ 20%]
test_cli_error_handling.py::TestPipelineErrorPropagation::test_adapter_execution_error_returns_exit_code_1 PASSED [ 26%]
test_cli_error_handling.py::TestPipelineErrorPropagation::test_pipeline_error_with_custom_exit_code PASSED       [ 33%]
test_cli_error_handling.py::TestPipelineErrorPropagation::test_pipeline_error_prints_to_stderr PASSED            [ 40%]
test_cli_error_handling.py::TestKeyboardInterruptHandling::test_keyboard_interrupt_returns_exit_runtime_error PASSED [ 46%]
test_cli_error_handling.py::TestKeyboardInterruptHandling::test_keyboard_interrupt_prints_to_stderr PASSED       [ 53%]
test_cli_error_handling.py::TestUnexpectedExceptionHandling::test_unexpected_exception_returns_exit_runtime_error PASSED [ 60%]
test_cli_error_handling.py::TestUnexpectedExceptionHandling::test_unexpected_exception_prints_to_stderr PASSED   [ 66%]
test_cli_error_handling.py::TestUnexpectedExceptionHandling::test_type_error_returns_exit_runtime_error PASSED   [ 73%]
test_cli_error_handling.py::TestDebugStackTrace::test_debug_flag_prints_traceback_on_pipeline_error PASSED       [ 80%]
test_cli_error_handling.py::TestDebugStackTrace::test_debug_flag_prints_traceback_on_unexpected_exception PASSED [ 86%]
test_cli_error_handling.py::TestDebugStackTrace::test_no_debug_flag_omits_traceback_on_pipeline_error PASSED     [ 93%]
test_cli_error_handling.py::TestDebugStackTrace::test_no_debug_flag_omits_traceback_on_unexpected_exception PASSED [100%]

15 passed in 0.15s
```


### 4. Report Lifecycle (`test_report_lifecycle.py`) — 13 passed

Covers skip, success, and failure report paths plus results.json update isolation.

```
test session starts
platform darwin -- Python 3.11.14, pytest-9.0.2

test_report_lifecycle.py::TestSkipReport::test_skip_report_returns_skipped_status PASSED              [  7%]
test_report_lifecycle.py::TestSkipReport::test_skip_report_produces_no_html PASSED                    [ 15%]
test_report_lifecycle.py::TestSkipReport::test_skip_report_updates_results_json PASSED                [ 23%]
test_report_lifecycle.py::TestSuccessfulReport::test_success_returns_report_path_and_status PASSED    [ 30%]
test_report_lifecycle.py::TestSuccessfulReport::test_success_writes_html_file PASSED                  [ 38%]
test_report_lifecycle.py::TestSuccessfulReport::test_success_updates_results_json PASSED              [ 46%]
test_report_lifecycle.py::TestReportFailure::test_failure_returns_none_and_failed_status PASSED       [ 53%]
test_report_lifecycle.py::TestReportFailure::test_failure_preserves_trace_eval_unchanged PASSED       [ 61%]
test_report_lifecycle.py::TestReportFailure::test_failure_updates_results_status_to_failed PASSED     [ 69%]
test_report_lifecycle.py::TestReportFailure::test_failure_does_not_flip_run_return_code PASSED        [ 76%]
test_report_lifecycle.py::TestUpdateResultsFailure::test_update_failure_logs_warning_and_continues PASSED [ 84%]
test_report_lifecycle.py::TestUpdateResultsFailure::test_update_failure_on_success_path_still_returns_success PASSED [ 92%]
test_report_lifecycle.py::TestUpdateResultsFailure::test_update_failure_on_failed_path_still_returns_failed PASSED [100%]

13 passed in 0.33s
```

### 5. Pipeline Input Detection (`test_pipeline_detection.py`) — 17 passed

Tests the heuristic that classifies input as "normalized" vs "raw" and boundary cases.

```
test session starts
platform darwin -- Python 3.11.14, pytest-9.0.2

test_pipeline_detection.py::TestNormalizedDetection::test_valid_normalized_run_classified_as_normalized PASSED [  5%]
test_pipeline_detection.py::TestRawDetection::test_raw_json_no_normalized_keys_classified_as_raw PASSED       [ 11%]
test_pipeline_detection.py::TestRawDetection::test_raw_json_with_unrelated_keys_classified_as_raw PASSED      [ 17%]
test_pipeline_detection.py::TestMalformedNormalizedDetection::test_two_normalized_keys_invalid_schema_raises_validation_error PASSED [ 23%]
test_pipeline_detection.py::TestMalformedNormalizedDetection::test_all_four_normalized_keys_invalid_values_raises_validation_error PASSED [ 29%]
test_pipeline_detection.py::TestMalformedNormalizedDetection::test_three_normalized_keys_raises_validation_error PASSED [ 35%]
test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_metadata_key_classified_as_raw PASSED       [ 41%]
test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_run_id_key_classified_as_raw PASSED         [ 47%]
test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_turns_key_classified_as_raw PASSED          [ 52%]
test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_adapter_stats_key_classified_as_raw PASSED  [ 58%]
test_pipeline_detection.py::TestHeuristicBoundaryTwoKeys::test_run_id_plus_turns_invalid_raises_validation_error PASSED [ 64%]
test_pipeline_detection.py::TestHeuristicBoundaryTwoKeys::test_metadata_plus_adapter_stats_invalid_raises_validation_error PASSED [ 70%]
test_pipeline_detection.py::TestInvalidJsonDetection::test_malformed_json_raises_validation_error PASSED       [ 76%]
test_pipeline_detection.py::TestInvalidJsonDetection::test_truncated_json_raises_validation_error PASSED       [ 82%]
test_pipeline_detection.py::TestInvalidJsonDetection::test_empty_file_raises_validation_error PASSED           [ 88%]
test_pipeline_detection.py::TestMissingValidatorModule::test_missing_schema_file_raises_config_error PASSED    [ 94%]
test_pipeline_detection.py::TestMissingValidatorModule::test_attribute_error_in_validator_raises_config_error PASSED [100%]

17 passed in 0.21s
```

---

## Full Suite Summary

```
$ pytest agent-eval/tests/system/ -v --tb=no -q
280 passed in 5.11s

$ pytest agent-eval/tests/ -v --tb=no -q
1 failed, 429 passed in 8.35s
```

The 1 failure is the pre-existing `test_autoescape_enabled_in_template_rendering` — unrelated to this spec.


---

## Appendix A: Git Diff — No Production Code Modified by This Spec

The 3 modified files under `agent_eval/` are from prior specs (runner-correctness-fixes, html-report-generation, etc.) and were already in the working tree before this system testing spec began. This spec added only test and spec files.

```
$ git diff --name-only HEAD -- agent-eval/agent_eval/
agent-eval/agent_eval/cli.py                          # Prior spec: runner-correctness-fixes
agent-eval/agent_eval/evaluators/trace_eval/runner.py  # Prior spec: runner-correctness-fixes
agent-eval/agent_eval/pipeline.py                      # Prior spec: runner-correctness-fixes
```

All system test files are untracked (new additions by this spec):

```
$ git status --short agent-eval/tests/system/
?? agent-eval/tests/system/

$ git status --short .kiro/specs/comprehensive-system-testing/
?? .kiro/specs/comprehensive-system-testing/
```

No file under `agent-eval/agent_eval/` was created or modified by this spec. The entire `tests/system/` directory and the spec directory are new untracked additions.

## Appendix B: Pre-Existing Failure Confirmation

The single failure across the full suite is in `test_security_requirements.py`, a test file created by the html-report-generation spec. It fails because `ReportViewModel.__init__()` no longer accepts a `generated_at` keyword argument — the parameter was removed during a prior refactor of `report_models.py`.

```
$ pytest agent-eval/tests/test_security_requirements.py::TestJinja2Autoescape::test_autoescape_enabled_in_template_rendering -v --tb=short

FAILED - TypeError: ReportViewModel.__init__() got an unexpected keyword argument 'generated_at'
```

Root cause evidence:

- `report_models.py` does not contain `generated_at` anywhere (confirmed via grep)
- `test_security_requirements.py` line 507 passes `generated_at=datetime.now()` to `ReportViewModel()`
- Both files are untracked (`??`) — created by the html-report-generation spec, not by this system testing spec
- This mismatch existed before any system test was written

This failure is not introduced by this branch's system testing work and requires a separate fix to align the test with the current `ReportViewModel` constructor signature.
