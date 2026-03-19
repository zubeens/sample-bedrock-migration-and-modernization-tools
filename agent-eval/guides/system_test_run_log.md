# System Test Run Log

Date: Thu Mar 19 2026

Reference: [SYSTEM_TESTING_EVIDENCE.md](SYSTEM_TESTING_EVIDENCE.md)

---

## Command 1: Full System Suite

```
pytest agent-eval/tests/system/ -v --tb=short
```

```
============================= test session starts ==============================
platform darwin -- Python 3.11.14, pytest-9.0.2, pluggy-1.6.0
plugins: anyio-4.12.1, hypothesis-6.151.5, cov-7.0.0
collected 280 items

agent-eval/tests/system/test_aggregation_filtering.py::TestGate1MalformedJson::test_malformed_json_line_skipped PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate1MalformedJson::test_multiple_malformed_json_lines PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[job_id] PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[rubric_id] PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[judge_id] PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[status] PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate3BadJobResult::test_invalid_status_value_skipped PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate3BadJobResult::test_missing_timestamp_skipped PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate4RunIdMismatch::test_different_run_id_skipped PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate4RunIdMismatch::test_matching_run_id_accepted PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate4RunIdMismatch::test_empty_run_id_accepted PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate4RunIdMismatch::test_none_run_id_accepted PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate4RunIdMismatch::test_mixed_run_ids_filters_correctly PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate5EmptyTurnIdNormalized::test_empty_turn_id_normalized_to_none PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate5EmptyTurnIdNormalized::test_non_empty_turn_id_preserved PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestNoValidRuns::test_all_lines_malformed_returns_empty PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestNoValidRuns::test_all_lines_wrong_run_id_returns_empty PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestNoValidRuns::test_empty_jsonl_returns_empty PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestNoValidRuns::test_mixed_failures_all_filtered_returns_empty PASSED
agent-eval/tests/system/test_aggregation_scoring.py::TestScoringScaleAsDict::test_dict_scoring_scale_numeric PASSED
agent-eval/tests/system/test_aggregation_scoring.py::TestScoringScaleAsDict::test_dict_scoring_scale_categorical PASSED
agent-eval/tests/system/test_aggregation_scoring.py::TestScoringScaleAsDataclass::test_dataclass_scoring_scale_numeric PASSED
agent-eval/tests/system/test_aggregation_scoring.py::TestScoringScaleAsDataclass::test_dataclass_scoring_scale_categorical PASSED
agent-eval/tests/system/test_aggregation_scoring.py::TestScoringScaleAsGenericObject::test_generic_object_scoring_scale PASSED
agent-eval/tests/system/test_aggregation_scoring.py::TestScoringScaleAsGenericObject::test_generic_object_with_rubric_object PASSED
agent-eval/tests/system/test_aggregation_scoring.py::TestNoScoringScale::test_none_scoring_scale_numeric PASSED
agent-eval/tests/system/test_aggregation_scoring.py::TestNoScoringScale::test_explicit_none_scoring_scale PASSED
agent-eval/tests/system/test_aggregation_scoring.py::TestNoScoringScale::test_none_scoring_scale_categorical PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestResultDictKeys::test_keys_present_with_valid_records PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestResultDictKeys::test_keys_present_with_empty_jsonl PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestResultDictKeys::test_keys_present_with_all_lines_filtered PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestCrossJudgeResultsAlias::test_semantic_equality_with_valid_records PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestCrossJudgeResultsAlias::test_semantic_equality_when_empty PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestTotalJobsEqualsLinesParsed::test_total_jobs_matches_lines_parsed_all_valid PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestTotalJobsEqualsLinesParsed::test_total_jobs_matches_lines_parsed_with_skips PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestTotalJobsEqualsLinesParsed::test_total_jobs_zero_when_empty PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestUnknownRubricIds::test_unknown_rubric_id_tracked PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestUnknownRubricIds::test_known_rubric_id_not_tracked PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestUnknownRubricIds::test_multiple_unknown_rubric_ids PASSED
agent-eval/tests/system/test_aggregation_structure.py::TestUnknownRubricIds::test_no_unknown_rubric_ids_when_empty_jsonl PASSED
agent-eval/tests/system/test_atomic_update.py::TestSuccessfulAtomicUpdate::test_successful_update_returns_true PASSED
agent-eval/tests/system/test_atomic_update.py::TestSuccessfulAtomicUpdate::test_successful_update_writes_report_path PASSED
agent-eval/tests/system/test_atomic_update.py::TestSuccessfulAtomicUpdate::test_successful_update_writes_report_status PASSED
agent-eval/tests/system/test_atomic_update.py::TestSuccessfulAtomicUpdate::test_successful_update_with_skipped_status PASSED
agent-eval/tests/system/test_atomic_update.py::TestSuccessfulAtomicUpdate::test_successful_update_with_failed_status PASSED
agent-eval/tests/system/test_atomic_update.py::TestSuccessfulAtomicUpdate::test_successful_update_initializes_missing_artifact_paths PASSED
agent-eval/tests/system/test_atomic_update.py::TestSuccessfulAtomicUpdate::test_successful_update_initializes_missing_execution_stats PASSED
agent-eval/tests/system/test_atomic_update.py::TestOperationalErrorsReturnFalse::test_missing_results_json_returns_false PASSED
agent-eval/tests/system/test_atomic_update.py::TestOperationalErrorsReturnFalse::test_json_decode_error_returns_false PASSED
agent-eval/tests/system/test_atomic_update.py::TestOperationalErrorsReturnFalse::test_oserror_on_read_returns_false PASSED
agent-eval/tests/system/test_atomic_update.py::TestOperationalErrorsReturnFalse::test_oserror_on_write_returns_false_and_preserves_original PASSED
agent-eval/tests/system/test_atomic_update.py::TestOperationalErrorsReturnFalse::test_oserror_on_fsync_returns_false PASSED
agent-eval/tests/system/test_atomic_update.py::TestOperationalErrorsReturnFalse::test_oserror_on_replace_returns_false PASSED
agent-eval/tests/system/test_atomic_update.py::TestOperationalErrorsReturnFalse::test_value_error_returns_false PASSED
agent-eval/tests/system/test_atomic_update.py::TestProgrammerBugsPropagate::test_key_error_propagates PASSED
agent-eval/tests/system/test_atomic_update.py::TestProgrammerBugsPropagate::test_type_error_propagates PASSED
agent-eval/tests/system/test_atomic_update.py::TestProgrammerBugsPropagate::test_attribute_error_propagates PASSED
agent-eval/tests/system/test_atomic_update.py::TestProgrammerBugsPropagate::test_runtime_error_propagates PASSED
agent-eval/tests/system/test_atomic_update.py::TestProgrammerBugsPropagate::test_index_error_propagates PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestChecksumKeyPrecedence::test_prefers_artifact_checksums_when_present PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestChecksumKeyPrecedence::test_falls_back_to_artifact_hashes_when_no_checksums PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestChecksumKeyPrecedence::test_artifact_checksums_takes_precedence_over_artifact_hashes PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestChecksumKeyPrecedence::test_initializes_artifact_checksums_when_neither_key_exists PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestChecksumRecomputation::test_checksums_recomputed_for_all_listed_artifacts PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestChecksumRecomputation::test_results_key_skipped_during_recomputation PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestChecksumRecomputation::test_empty_artifact_path_skipped PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestNoSelfHash::test_no_results_key_in_checksum_map PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestNoSelfHash::test_no_results_key_even_with_legacy_hashes PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestMissingArtifactChecksum::test_missing_artifact_sets_checksum_to_none PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestMissingArtifactChecksum::test_all_missing_artifacts_set_to_none PASSED
agent-eval/tests/system/test_checksum_resolution.py::TestMissingArtifactChecksum::test_missing_artifact_does_not_crash PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestEntrypointDelegation::test_trace_eval_cli_delegates_to_run_via_pipeline PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestEntrypointDelegation::test_eval_pipeline_cli_delegates_to_run_via_pipeline PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestEntrypointDelegation::test_both_entrypoints_delegate_to_same_function PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestExitCodePassthrough::test_trace_eval_cli_returns_pipeline_exit_code[0] PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestExitCodePassthrough::test_trace_eval_cli_returns_pipeline_exit_code[1] PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestExitCodePassthrough::test_trace_eval_cli_returns_pipeline_exit_code[2] PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestExitCodePassthrough::test_trace_eval_cli_returns_pipeline_exit_code[3] PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestExitCodePassthrough::test_trace_eval_cli_returns_pipeline_exit_code[4] PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestExitCodePassthrough::test_eval_pipeline_cli_returns_pipeline_exit_code[0] PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestExitCodePassthrough::test_eval_pipeline_cli_returns_pipeline_exit_code[1] PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestExitCodePassthrough::test_eval_pipeline_cli_returns_pipeline_exit_code[2] PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestExitCodePassthrough::test_eval_pipeline_cli_returns_pipeline_exit_code[3] PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestExitCodePassthrough::test_eval_pipeline_cli_returns_pipeline_exit_code[4] PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestSharedFlags::test_trace_eval_cli_accepts_skip_report PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestSharedFlags::test_eval_pipeline_cli_accepts_skip_report PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestSharedFlags::test_trace_eval_cli_accepts_no_charts PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestSharedFlags::test_eval_pipeline_cli_accepts_no_charts PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestSharedFlags::test_trace_eval_cli_accepts_verbose PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestSharedFlags::test_eval_pipeline_cli_accepts_verbose PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestSharedFlags::test_trace_eval_cli_accepts_debug PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestSharedFlags::test_eval_pipeline_cli_accepts_debug PASSED
agent-eval/tests/system/test_cli_entrypoint.py::TestSharedFlags::test_defaults_without_optional_flags PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestPipelineErrorPropagation::test_pipeline_error_returns_its_exit_code PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestPipelineErrorPropagation::test_pipeline_validation_error_returns_exit_code_4 PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestPipelineErrorPropagation::test_pipeline_config_error_returns_exit_code_3 PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestPipelineErrorPropagation::test_adapter_execution_error_returns_exit_code_1 PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestPipelineErrorPropagation::test_pipeline_error_with_custom_exit_code PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestPipelineErrorPropagation::test_pipeline_error_prints_to_stderr PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestKeyboardInterruptHandling::test_keyboard_interrupt_returns_exit_runtime_error PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestKeyboardInterruptHandling::test_keyboard_interrupt_prints_to_stderr PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestUnexpectedExceptionHandling::test_unexpected_exception_returns_exit_runtime_error PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestUnexpectedExceptionHandling::test_unexpected_exception_prints_to_stderr PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestUnexpectedExceptionHandling::test_type_error_returns_exit_runtime_error PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestDebugStackTrace::test_debug_flag_prints_traceback_on_pipeline_error PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestDebugStackTrace::test_debug_flag_prints_traceback_on_unexpected_exception PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestDebugStackTrace::test_no_debug_flag_omits_traceback_on_pipeline_error PASSED
agent-eval/tests/system/test_cli_error_handling.py::TestDebugStackTrace::test_no_debug_flag_omits_traceback_on_unexpected_exception PASSED
agent-eval/tests/system/test_cli_validation.py::TestNonexistentInputFile::test_nonexistent_input_returns_exit_code_4 PASSED
agent-eval/tests/system/test_cli_validation.py::TestNonexistentJudgeConfig::test_nonexistent_judge_config_returns_exit_code_3 PASSED
agent-eval/tests/system/test_cli_validation.py::TestMultipleErrorSeverity::test_validation_and_config_errors_returns_most_severe PASSED
agent-eval/tests/system/test_cli_validation.py::TestMultipleErrorSeverity::test_config_only_error_returns_config_code PASSED
agent-eval/tests/system/test_cli_validation.py::TestOutputDirResolution::test_successful_validation_resolves_output_dir PASSED
agent-eval/tests/system/test_cli_validation.py::TestNamespaceImmutabilityOnFailure::test_failed_validation_leaves_args_unmutated PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_pipeline_succeeds PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_produces_all_artifacts PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_report_generated_when_not_skipped PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_result_paths_point_to_existing_files PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_pipeline_succeeds PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_produces_same_artifacts_as_raw PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_report_generated PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_result_paths_valid PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EErrorScenarios::test_adapter_failure_raises_with_exit_code_1 PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EErrorScenarios::test_report_failure_still_returns_success PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EErrorScenarios::test_skip_report_returns_success_no_html PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EDegradedAggregation::test_degraded_aggregation_succeeds_with_partial_results PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EArtifactPathReportingOnFailure::test_failure_after_partial_artifacts_reports_existing_paths PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EArtifactPathReportingOnFailure::test_failure_reports_none_for_missing_artifacts PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EArtifactPathReportingOnFailure::test_failure_existing_artifact_paths_are_accessible PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_alphanumeric_and_symbols[simple] PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_alphanumeric_and_symbols[test-run-001] PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_alphanumeric_and_symbols[my_run.v2] PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_alphanumeric_and_symbols[ABC123] PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_alphanumeric_and_symbols[a] PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_alphanumeric_and_symbols[run-2025.01.15-abc] PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_alphanumeric_and_symbols[Z] PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_alphanumeric_and_symbols[hello-world] PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_alphanumeric_and_symbols[some_thing] PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_chars_with_leading_dot_stripped PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_chars_with_trailing_dot_stripped PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_chars_with_leading_underscore_stripped PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_chars_with_trailing_underscore_stripped PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestSafeCharactersUnchanged::test_safe_chars_with_both_ends_stripped PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestUnsafeCharactersReplaced::test_slash_replaced PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestUnsafeCharactersReplaced::test_backslash_replaced PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestUnsafeCharactersReplaced::test_space_replaced PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestUnsafeCharactersReplaced::test_colon_replaced PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestUnsafeCharactersReplaced::test_multiple_unsafe_chars PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestUnsafeCharactersReplaced::test_path_traversal_replaced PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestUnsafeCharactersReplaced::test_special_chars_replaced PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestUnsafeCharactersReplaced::test_unicode_replaced PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestEmptyFallback::test_empty_string PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestEmptyFallback::test_only_dots PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestEmptyFallback::test_only_underscores PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestEmptyFallback::test_only_unsafe_chars PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestEmptyFallback::test_none_input PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestEmptyFallback::test_dots_and_underscores_mixed PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_truncation_to_max_length PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_custom_max_length PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_truncation_strips_trailing_dots PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_max_length_zero_returns_fallback PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_max_length_negative_returns_fallback PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_windows_reserved_con PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_windows_reserved_prn PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_windows_reserved_nul PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_windows_reserved_case_insensitive PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_non_string_int_coerced PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_non_string_float_coerced PASSED
agent-eval/tests/system/test_filename_sanitization.py::TestAdditionalBehavior::test_non_string_bool_coerced PASSED
agent-eval/tests/system/test_fixtures_smoke.py::TestHelperFunctions::test_write_json_creates_file PASSED
agent-eval/tests/system/test_fixtures_smoke.py::TestHelperFunctions::test_write_json_creates_parent_dirs PASSED
agent-eval/tests/system/test_fixtures_smoke.py::TestHelperFunctions::test_make_judge_runs_jsonl_creates_file PASSED
agent-eval/tests/system/test_fixtures_smoke.py::TestHelperFunctions::test_make_judge_runs_jsonl_empty_records PASSED
agent-eval/tests/system/test_fixtures_smoke.py::TestFixtures::test_tmp_output_dir_exists PASSED
agent-eval/tests/system/test_fixtures_smoke.py::TestFixtures::test_valid_judge_config_is_valid_yaml PASSED
agent-eval/tests/system/test_fixtures_smoke.py::TestFixtures::test_minimal_normalized_run_has_required_keys PASSED
agent-eval/tests/system/test_fixtures_smoke.py::TestFixtures::test_minimal_raw_trace_has_events PASSED
agent-eval/tests/system/test_output_artifacts.py::TestTraceEvalJsonContent::test_trace_eval_json_written PASSED
agent-eval/tests/system/test_output_artifacts.py::TestTraceEvalJsonContent::test_trace_eval_json_has_run_id PASSED
agent-eval/tests/system/test_output_artifacts.py::TestTraceEvalJsonContent::test_trace_eval_json_has_deterministic_metrics PASSED
agent-eval/tests/system/test_output_artifacts.py::TestTraceEvalJsonContent::test_trace_eval_json_has_rubric_results PASSED
agent-eval/tests/system/test_output_artifacts.py::TestTraceEvalJsonContent::test_trace_eval_json_has_judge_summary PASSED
agent-eval/tests/system/test_output_artifacts.py::TestResultsJsonContent::test_results_json_written PASSED
agent-eval/tests/system/test_output_artifacts.py::TestResultsJsonContent::test_results_json_has_run_id PASSED
agent-eval/tests/system/test_output_artifacts.py::TestResultsJsonContent::test_results_json_has_config_hashes PASSED
agent-eval/tests/system/test_output_artifacts.py::TestResultsJsonContent::test_results_json_has_artifact_paths PASSED
agent-eval/tests/system/test_output_artifacts.py::TestResultsJsonContent::test_results_json_has_execution_stats PASSED
agent-eval/tests/system/test_output_artifacts.py::TestResultsJsonContent::test_results_json_has_artifact_hashes PASSED
agent-eval/tests/system/test_output_artifacts.py::TestReportGenerationStatusPending::test_default_report_generation_status_is_pending PASSED
agent-eval/tests/system/test_output_artifacts.py::TestReportGenerationStatusPending::test_explicit_pending_status PASSED
agent-eval/tests/system/test_output_artifacts.py::TestReportGenerationStatusPending::test_report_path_is_none_before_step_11 PASSED
agent-eval/tests/system/test_pipeline_adapter.py::TestAdapterInvocation::test_raw_input_triggers_adapter_and_validates_output PASSED
agent-eval/tests/system/test_pipeline_adapter.py::TestAdapterErrorHandling::test_adapter_error_raises_adapter_execution_error PASSED
agent-eval/tests/system/test_pipeline_adapter.py::TestAdapterErrorHandling::test_adapter_input_error_raises_adapter_execution_error PASSED
agent-eval/tests/system/test_pipeline_adapter.py::TestAdapterErrorHandling::test_adapter_validation_error_raises_adapter_execution_error PASSED
agent-eval/tests/system/test_pipeline_adapter.py::TestAdapterOutputValidation::test_adapter_output_failing_schema_raises_pipeline_validation_error PASSED
agent-eval/tests/system/test_pipeline_adapter.py::TestAdapterOutputValidation::test_adapter_output_empty_dict_raises_pipeline_validation_error PASSED
agent-eval/tests/system/test_pipeline_adapter.py::TestUnexpectedAdapterExceptions::test_type_error_in_adapter_not_flattened_to_adapter_execution_error PASSED
agent-eval/tests/system/test_pipeline_adapter.py::TestUnexpectedAdapterExceptions::test_attribute_error_in_adapter_not_flattened_to_adapter_execution_error PASSED
agent-eval/tests/system/test_pipeline_adapter.py::TestUnexpectedAdapterExceptions::test_key_error_in_adapter_not_flattened_to_adapter_execution_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestNormalizedDetection::test_valid_normalized_run_classified_as_normalized PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestRawDetection::test_raw_json_no_normalized_keys_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestRawDetection::test_raw_json_with_unrelated_keys_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestMalformedNormalizedDetection::test_two_normalized_keys_invalid_schema_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestMalformedNormalizedDetection::test_all_four_normalized_keys_invalid_values_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestMalformedNormalizedDetection::test_three_normalized_keys_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_metadata_key_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_run_id_key_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_turns_key_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_adapter_stats_key_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryTwoKeys::test_run_id_plus_turns_invalid_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryTwoKeys::test_metadata_plus_adapter_stats_invalid_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestInvalidJsonDetection::test_malformed_json_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestInvalidJsonDetection::test_truncated_json_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestInvalidJsonDetection::test_empty_file_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestMissingValidatorModule::test_missing_schema_file_raises_config_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestMissingValidatorModule::test_attribute_error_in_validator_raises_config_error PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestResultPayloadKeys::test_result_dict_contains_all_required_keys_normalized_input PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestResultPayloadKeys::test_result_dict_contains_all_required_keys_raw_input PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestResultPayloadKeys::test_result_dict_keys_have_correct_types PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestSuccessEqualsExitCodeZero::test_success_true_when_exit_code_zero PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestSuccessEqualsExitCodeZero::test_success_false_when_exit_code_nonzero PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestSuccessEqualsExitCodeZero::test_success_false_for_various_nonzero_exit_codes[1-6] PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestArtifactPathExistence::test_trace_eval_path_non_none_when_file_exists PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestArtifactPathExistence::test_trace_eval_path_none_when_file_missing PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestArtifactPathExistence::test_results_path_non_none_when_file_exists PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestArtifactPathExistence::test_results_path_none_when_file_missing PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestArtifactPathExistence::test_report_path_non_none_when_file_exists PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestArtifactPathExistence::test_report_path_none_when_file_missing PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestArtifactPathExistence::test_all_artifact_paths_none_when_no_files_created PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestArtifactPathExistence::test_all_artifact_paths_non_none_when_all_files_created PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestArtifactPathExistence::test_partial_artifact_creation_mixed_paths PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestArtifactPathExistence::test_artifact_paths_reflect_disk_state_on_failure PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestPayloadCorrectness::test_input_format_is_normalized_for_normalized_input PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestPayloadCorrectness::test_input_format_is_raw_for_raw_input PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestPayloadCorrectness::test_normalized_path_exists_and_is_valid PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestPayloadCorrectness::test_output_dir_is_absolute_path PASSED
agent-eval/tests/system/test_pipeline_payload.py::TestPayloadCorrectness::test_run_id_matches_input_run_id PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestNormalizedArtifactWrittenOnce::test_exactly_one_normalized_artifact_for_normalized_input PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestNormalizedArtifactWrittenOnce::test_exactly_one_normalized_artifact_for_raw_input PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestNormalizedArtifactWrittenOnce::test_normalized_artifact_content_matches_input PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestSanitizedFilename::test_safe_run_id_uses_sanitize_filename PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestSanitizedFilename::test_unsafe_characters_in_run_id_are_sanitized PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestSanitizedFilename::test_dots_only_run_id_uses_fallback PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestFallbackRunId::test_missing_run_id_generates_fallback_with_timestamp_and_uuid PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestFallbackRunId::test_missing_run_id_still_writes_exactly_one_artifact PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestFallbackRunId::test_empty_string_run_id_generates_fallback PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestFallbackRunId::test_fallback_run_id_injected_into_persisted_artifact PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestRunnerDoesNotDuplicateArtifact::test_runner_receives_normalized_path_but_does_not_write_copy PASSED
agent-eval/tests/system/test_pipeline_persistence.py::TestRunnerDoesNotDuplicateArtifact::test_multiple_pipeline_runs_each_produce_one_artifact PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSkipReport::test_skip_report_returns_skipped_status PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSkipReport::test_skip_report_produces_no_html PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSkipReport::test_skip_report_updates_results_json PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSuccessfulReport::test_success_returns_report_path_and_status PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSuccessfulReport::test_success_writes_html_file PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSuccessfulReport::test_success_updates_results_json PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestReportFailure::test_failure_returns_none_and_failed_status PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestReportFailure::test_failure_preserves_trace_eval_unchanged PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestReportFailure::test_failure_updates_results_status_to_failed PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestReportFailure::test_failure_does_not_flip_run_return_code PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestUpdateResultsFailure::test_update_failure_logs_warning_and_continues PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestUpdateResultsFailure::test_update_failure_on_success_path_still_returns_success PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestUpdateResultsFailure::test_update_failure_on_failed_path_still_returns_failed PASSED
agent-eval/tests/system/test_report_preflight.py::TestReportPreflight::test_missing_trace_eval_raises_file_not_found PASSED
agent-eval/tests/system/test_report_preflight.py::TestReportPreflight::test_missing_results_raises_file_not_found PASSED
agent-eval/tests/system/test_report_preflight.py::TestReportPreflight::test_both_missing_raises_file_not_found_listing_both PASSED
agent-eval/tests/system/test_runner_config.py::TestMalformedJudgesYaml::test_invalid_yaml_syntax_raises_config_error PASSED
agent-eval/tests/system/test_runner_config.py::TestMalformedJudgesYaml::test_truncated_yaml_raises_config_error PASSED
agent-eval/tests/system/test_runner_config.py::TestZeroJudges::test_empty_judges_list_raises_config_error PASSED
agent-eval/tests/system/test_runner_config.py::TestZeroJudges::test_missing_judges_key_raises_config_error PASSED
agent-eval/tests/system/test_runner_config.py::TestFiveJudges::test_five_judges_loads_successfully PASSED
agent-eval/tests/system/test_runner_config.py::TestFiveJudges::test_six_judges_raises_config_error PASSED
agent-eval/tests/system/test_runner_config.py::TestInvalidUserRubrics::test_malformed_user_rubrics_yaml_raises_config_error PASSED
agent-eval/tests/system/test_runner_config.py::TestInvalidUserRubrics::test_user_rubrics_missing_rubrics_key_raises_config_error PASSED
agent-eval/tests/system/test_runner_config.py::TestDuplicateRubricIds::test_duplicate_rubric_ids_in_user_file_raises_config_error PASSED

============================= 280 passed in 5.60s ==============================
```

---

## Command 2: End-to-End Pipeline Scenarios

```
pytest agent-eval/tests/system/test_e2e_pipeline.py -v --tb=short
```

```
======================================================== test session starts ========================================================
platform darwin -- Python 3.11.14, pytest-9.0.2, pluggy-1.6.0
plugins: anyio-4.12.1, hypothesis-6.151.5, cov-7.0.0
collected 15 items

agent-eval/tests/system/test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_pipeline_succeeds PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_produces_all_artifacts PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_report_generated_when_not_skipped PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ERawInputSuccess::test_raw_input_result_paths_point_to_existing_files PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_pipeline_succeeds PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_produces_same_artifacts_as_raw PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_report_generated PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2ENormalizedInputSuccess::test_normalized_input_result_paths_valid PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EErrorScenarios::test_adapter_failure_raises_with_exit_code_1 PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EErrorScenarios::test_report_failure_still_returns_success PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EErrorScenarios::test_skip_report_returns_success_no_html PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EDegradedAggregation::test_degraded_aggregation_succeeds_with_partial_results PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EArtifactPathReportingOnFailure::test_failure_after_partial_artifacts_reports_existing_paths PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EArtifactPathReportingOnFailure::test_failure_reports_none_for_missing_artifacts PASSED
agent-eval/tests/system/test_e2e_pipeline.py::TestE2EArtifactPathReportingOnFailure::test_failure_existing_artifact_paths_are_accessible PASSED

======================================================== 15 passed in 1.72s =========================================================
```

---

## Command 3: Pipeline Detection Boundary Tests

```
pytest agent-eval/tests/system/test_pipeline_detection.py -v --tb=short
```

```
======================================================== test session starts ========================================================
platform darwin -- Python 3.11.14, pytest-9.0.2, pluggy-1.6.0
plugins: anyio-4.12.1, hypothesis-6.151.5, cov-7.0.0
collected 17 items

agent-eval/tests/system/test_pipeline_detection.py::TestNormalizedDetection::test_valid_normalized_run_classified_as_normalized PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestRawDetection::test_raw_json_no_normalized_keys_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestRawDetection::test_raw_json_with_unrelated_keys_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestMalformedNormalizedDetection::test_two_normalized_keys_invalid_schema_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestMalformedNormalizedDetection::test_all_four_normalized_keys_invalid_values_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestMalformedNormalizedDetection::test_three_normalized_keys_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_metadata_key_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_run_id_key_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_turns_key_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryOneKey::test_only_adapter_stats_key_classified_as_raw PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryTwoKeys::test_run_id_plus_turns_invalid_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestHeuristicBoundaryTwoKeys::test_metadata_plus_adapter_stats_invalid_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestInvalidJsonDetection::test_malformed_json_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestInvalidJsonDetection::test_truncated_json_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestInvalidJsonDetection::test_empty_file_raises_validation_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestMissingValidatorModule::test_missing_schema_file_raises_config_error PASSED
agent-eval/tests/system/test_pipeline_detection.py::TestMissingValidatorModule::test_attribute_error_in_validator_raises_config_error PASSED

======================================================== 17 passed in 0.26s =========================================================
```

---

## Command 4: Aggregation Gate Tests

```
pytest agent-eval/tests/system/test_aggregation_filtering.py -v --tb=short
```

```
======================================================== test session starts ========================================================
platform darwin -- Python 3.11.14, pytest-9.0.2, pluggy-1.6.0
plugins: anyio-4.12.1, hypothesis-6.151.5, cov-7.0.0
collected 19 items

agent-eval/tests/system/test_aggregation_filtering.py::TestGate1MalformedJson::test_malformed_json_line_skipped PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate1MalformedJson::test_multiple_malformed_json_lines PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[job_id] PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[rubric_id] PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[judge_id] PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate2MissingFields::test_missing_required_field_skipped[status] PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate3BadJobResult::test_invalid_status_value_skipped PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate3BadJobResult::test_missing_timestamp_skipped PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate4RunIdMismatch::test_different_run_id_skipped PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate4RunIdMismatch::test_matching_run_id_accepted PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate4RunIdMismatch::test_empty_run_id_accepted PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate4RunIdMismatch::test_none_run_id_accepted PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate4RunIdMismatch::test_mixed_run_ids_filters_correctly PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate5EmptyTurnIdNormalized::test_empty_turn_id_normalized_to_none PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestGate5EmptyTurnIdNormalized::test_non_empty_turn_id_preserved PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestNoValidRuns::test_all_lines_malformed_returns_empty PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestNoValidRuns::test_all_lines_wrong_run_id_returns_empty PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestNoValidRuns::test_empty_jsonl_returns_empty PASSED
agent-eval/tests/system/test_aggregation_filtering.py::TestNoValidRuns::test_mixed_failures_all_filtered_returns_empty PASSED

======================================================== 19 passed in 0.55s =========================================================
```

---

## Command 5: Report Lifecycle Tests

```
pytest agent-eval/tests/system/test_report_lifecycle.py -v --tb=short
```

```
======================================================== test session starts ========================================================
platform darwin -- Python 3.11.14, pytest-9.0.2, pluggy-1.6.0
plugins: anyio-4.12.1, hypothesis-6.151.5, cov-7.0.0
collected 13 items

agent-eval/tests/system/test_report_lifecycle.py::TestSkipReport::test_skip_report_returns_skipped_status PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSkipReport::test_skip_report_produces_no_html PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSkipReport::test_skip_report_updates_results_json PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSuccessfulReport::test_success_returns_report_path_and_status PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSuccessfulReport::test_success_writes_html_file PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestSuccessfulReport::test_success_updates_results_json PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestReportFailure::test_failure_returns_none_and_failed_status PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestReportFailure::test_failure_preserves_trace_eval_unchanged PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestReportFailure::test_failure_updates_results_status_to_failed PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestReportFailure::test_failure_does_not_flip_run_return_code PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestUpdateResultsFailure::test_update_failure_logs_warning_and_continues PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestUpdateResultsFailure::test_update_failure_on_success_path_still_returns_success PASSED
agent-eval/tests/system/test_report_lifecycle.py::TestUpdateResultsFailure::test_update_failure_on_failed_path_still_returns_failed PASSED

======================================================== 13 passed in 1.91s =========================================================
```

---

## Summary

| Command | Suite | Tests | Passed | Failed | Skipped | Time |
|---------|-------|-------|--------|--------|---------|------|
| 1 | Full system suite | 280 | 280 | 0 | 0 | 5.60s |
| 2 | E2E pipeline scenarios | 15 | 15 | 0 | 0 | 1.72s |
| 3 | Pipeline detection boundary | 17 | 17 | 0 | 0 | 0.26s |
| 4 | Aggregation gate tests | 19 | 19 | 0 | 0 | 0.55s |
| 5 | Report lifecycle | 13 | 13 | 0 | 0 | 1.91s |

All 280 system tests passed. Zero failures, zero skips, zero xfails.
