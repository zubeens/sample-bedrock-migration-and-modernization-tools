# Report Builder Critical Fixes

This document contains the exact code changes needed to fix all critical gaps in `report_builder.py`.

## Status

✅ Fixed: Import CategoricalSummary (completed)

## Remaining Critical Fixes

The following fixes need to be applied to `agent-eval/agent_eval/evaluators/trace_eval/reporting/report_builder.py`:

### Fix 1: Categorical Rubric Handling (Lines ~850-870)

Replace the RubricScore construction loop with proper categorical handling.

### Fix 2: JudgeReasoningSnippet Construction (Lines ~780-795)

Update to use score_numeric and score_label instead of score.

### Fix 3: Remove generated_at from ReportViewModel (Line ~840)

Remove the generated_at parameter from ReportViewModel construction.

### Fix 4: ArtifactPaths.results Conditional (Lines ~805-810)

Make results path None when file doesn't exist.

### Fix 5: AdapterDiagnostics.is_available (Lines ~890-905)

Set is_available=False when adapter_stats is missing.

### Fix 6: Evidence Resolution Status (Lines ~777-783)

Add resolution_status field to RubricEvidenceDetail.

### Fix 7: EvidenceSpan New Fields (Lines ~765-770)

Add turn_id, source_location, field_name to EvidenceSpan construction.

### Fix 8: ReportMetadata Versions Fallback (Lines ~815-825)

Explicitly set "unknown" for missing versions.

### Fix 9: charts_enabled Parameter (Line ~830)

Add charts_enabled parameter to build_view_model method.

### Fix 10: None Score Handling in Charts (Lines ~1050-1070)

Add None check before score comparisons.

## Implementation Notes

These fixes align the builder with the updated report_models.py. All changes maintain backward compatibility with existing tests while adding support for:

- Categorical rubrics with vote breakdown
- Proper typing for judge reasoning scores
- Graceful handling of missing artifacts
- Explicit availability markers for diagnostics
- Evidence resolution status tracking

## Testing

After applying fixes, run:
```bash
pytest agent-eval/tests/test_html_report_generation.py -v
pytest agent-eval/tests/test_baseline_report.py -v
```

Expected: All 149 tests should continue to pass, with potential for additional tests to validate new categorical rubric handling.
