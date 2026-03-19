# Report Builder Gaps Summary

This document summarizes all identified gaps in `report_builder.py` that need to be fixed to align with the updated `report_models.py`.

## Critical Gaps (Will Cause Runtime Errors)

### 1. Missing CategoricalSummary Import
**Location:** Line ~730 (imports section)
**Issue:** `CategoricalSummary` is not imported but is needed for categorical rubric handling
**Fix:** Add `CategoricalSummary` to the import statement from report_models

### 2. Categorical Rubric Handling Broken in build_view_model()
**Location:** Lines ~850-870 (RubricScore construction)
**Issue:** 
- `RubricScore` now expects `categorical_summary` field but builder never populates it
- For categorical rubrics, `cross_judge_score` should be `None`, not `weighted_vote`
- `disagreement_signal` should be `Optional[float]` (may be None for categorical)

**Fix:**
```python
# For categorical rubrics
if is_categorical:
    # Build categorical summary
    vote_breakdown = {}  # Extract from within_judge_results
    aggregated_label = cross_judge.get('aggregated_label')  # or derive from votes
    disagreement_text = "..."  # Derive from vote dispersion
    
    categorical_summary = CategoricalSummary(
        aggregated_label=aggregated_label,
        vote_breakdown=vote_breakdown,
        disagreement_text=disagreement_text
    )
    
    score = RubricScore(
        rubric_id=rubric_result.get('rubric_id', 'unknown'),
        scope=rubric_result.get('scope', 'run'),
        turn_id=rubric_result.get('turn_id'),
        cross_judge_score=None,  # None for categorical
        disagreement_signal=cross_judge.get('disagreement_signal'),  # May be None
        high_risk_flag=cross_judge.get('high_risk_flag', False),
        judge_count=cross_judge.get('judge_count', 0),
        scoring_type=scoring_type,
        is_categorical=True,
        categorical_summary=categorical_summary
    )
else:
    # Numeric rubrics
    score = RubricScore(
        rubric_id=rubric_result.get('rubric_id', 'unknown'),
        scope=rubric_result.get('scope', 'run'),
        turn_id=rubric_result.get('turn_id'),
        cross_judge_score=cross_judge.get('weighted_average', 0.0),
        disagreement_signal=cross_judge.get('disagreement_signal', 0.0),
        high_risk_flag=cross_judge.get('high_risk_flag', False),
        judge_count=cross_judge.get('judge_count', 0),
        scoring_type=scoring_type,
        is_categorical=False,
        categorical_summary=None
    )
```

### 3. JudgeReasoningSnippet Construction Outdated
**Location:** Lines ~780-795 (judge reasoning extraction)
**Issue:** Model now expects `score_numeric` and `score_label` instead of `score`

**Fix:**
```python
for judge_result in within_judge_results:
    judge_id = judge_result.get('judge_id', 'unknown')
    score = judge_result.get('score')
    reasoning = judge_result.get('reasoning', '')
    
    # Create reasoning preview (max 200 chars)
    reasoning_preview = reasoning[:200]
    if len(reasoning) > 200:
        reasoning_preview += '...'
    
    # Determine if score is numeric or categorical
    if is_categorical:
        snippet = JudgeReasoningSnippet(
            judge_id=judge_id,
            score_numeric=None,
            score_label=str(score) if score is not None else None,
            reasoning=reasoning,
            reasoning_preview=reasoning_preview
        )
    else:
        snippet = JudgeReasoningSnippet(
            judge_id=judge_id,
            score_numeric=float(score) if score is not None else None,
            score_label=None,
            reasoning=reasoning,
            reasoning_preview=reasoning_preview
        )
    reasoning_snippets.append(snippet)
```

### 4. ReportViewModel(generated_at=...) Removed
**Location:** Line ~840 (ReportViewModel construction)
**Issue:** Model no longer has `generated_at` field (removed as redundant with report_metadata.generation_timestamp)

**Fix:** Remove `generated_at=datetime.now()` from ReportViewModel construction

### 5. ArtifactPaths.results Should Be None When Missing
**Location:** Lines ~805-810 (ArtifactPaths construction)
**Issue:** Builder always sets string path for results, even if results.json is absent

**Fix:**
```python
# Check if results.json exists
results_path_str = None
if (self.output_dir / "results.json").exists():
    results_path_str = str(self.output_dir / "results.json")

artifact_paths = ArtifactPaths(
    normalized_run=str(self.output_dir / f"normalized_run.{self.safe_run_id}.json"),
    trace_eval=str(self.output_dir / "trace_eval.json"),
    judge_runs=str(self.output_dir / "judge_runs.jsonl"),
    results=results_path_str,  # None if file doesn't exist
    report=None,  # Doesn't exist yet before write
    checksums=checksums
)
```

### 6. AdapterDiagnostics.is_available Not Set Correctly
**Location:** Lines ~890-905 (AdapterDiagnostics construction)
**Issue:** When adapter_stats is missing, builder creates empty diagnostics but doesn't set `is_available=False`

**Fix:**
```python
if adapter_stats is None:
    self.logger("⚠ Warning: adapter_stats missing from normalized_run, creating empty diagnostics")
    adapter_diagnostics = AdapterDiagnostics(
        total_events_processed=0,
        events_with_valid_timestamps=0,
        dropped_events_count=0,
        invalid_events_count=0,
        confidence_penalties=[],
        orphan_tool_results=[],
        warnings=[],
        missing_fields_summary={},
        is_available=False  # Mark as unavailable
    )
else:
    adapter_diagnostics = AdapterDiagnostics(
        total_events_processed=adapter_stats.get('total_events_processed', 0),
        events_with_valid_timestamps=adapter_stats.get('events_with_valid_timestamps', 0),
        dropped_events_count=adapter_stats.get('dropped_events_count', 0),
        invalid_events_count=adapter_stats.get('invalid_events_count', 0),
        confidence_penalties=adapter_stats.get('confidence_penalties', []),
        orphan_tool_results=adapter_stats.get('orphan_tool_results', []),
        warnings=adapter_stats.get('warnings', []),
        missing_fields_summary=adapter_stats.get('missing_fields_summary', {}),
        is_available=True  # Mark as available
    )
```

## Medium Priority Gaps

### 7. ReportMetadata.source_artifact_versions Fallback Incomplete
**Location:** Lines ~815-825 (ReportMetadata construction)
**Issue:** If versions are missing, should explicitly populate "unknown" per plan, not leave sparse dicts

**Fix:**
```python
# Extract source artifact versions with explicit "unknown" fallback
source_versions = {
    'adapter_version': 'unknown',
    'trace_eval_version': 'unknown',
    'generator_version': '1.0.0'
}

if metadata:
    source_versions['adapter_version'] = metadata.get('adapter_version', 'unknown')

if 'version' in trace_eval:
    source_versions['trace_eval_version'] = trace_eval.get('version', 'unknown')
```

### 8. report_metadata.charts_enabled Hardcoded
**Location:** Line ~830 (ReportMetadata construction)
**Issue:** `charts_enabled=True` is hardcoded, should come from caller/actual chart generation state

**Fix:** Add parameter to `build_view_model()`:
```python
def build_view_model(self, artifacts: Dict[str, Any], charts_enabled: bool = True) -> 'ReportViewModel':
    # ...
    report_metadata = ReportMetadata(
        generator_version=generator_version,
        generation_timestamp=datetime.now(),
        source_artifact_versions=source_versions,
        charts_enabled=charts_enabled,  # From parameter
        template_version="1.0.0"
    )
```

### 9. Evidence Resolution Not Implemented
**Location:** Lines ~755-775 (evidence resolution)
**Issue:** Only writes placeholder text: "[Evidence resolution not yet implemented]"

**Status:** This is the biggest functional gap vs the plan. Full implementation would require:
- Selector parsing engine
- Context resolution against normalized_run
- Turn-scoped vs run-scoped resolution
- Field name extraction

**Recommendation:** Document as known limitation or implement in separate task

### 10. EvidenceSpan Missing New Fields
**Location:** Lines ~765-770 (EvidenceSpan construction)
**Issue:** Model now has `turn_id`, `source_location`, `field_name` fields that aren't populated

**Fix:**
```python
evidence_span = EvidenceSpan(
    selector=str(selector),
    resolved_content="[Evidence resolution not yet implemented]",
    context_type=scope,
    turn_id=turn_id if scope == "turn" else None,
    source_location=None,  # Would be populated by full resolution
    field_name=None  # Would be extracted from selector
)
```

### 11. RubricEvidenceDetail Missing resolution_status
**Location:** Lines ~777-783 (RubricEvidenceDetail construction)
**Issue:** Model now has `resolution_status` field with default "success"

**Fix:**
```python
# Determine resolution status
if not selectors:
    resolution_status = "selectors_missing"
elif not evidence_spans:
    resolution_status = "resolution_failed"
elif len(evidence_spans) < len(selectors):
    resolution_status = "partial"
else:
    resolution_status = "success"

evidence_detail = RubricEvidenceDetail(
    rubric_id=rubric_id,
    scope=scope,
    turn_id=turn_id,
    evidence_spans=evidence_spans,
    evidence_fields_used=evidence_fields_used,
    resolution_status=resolution_status
)
```

## Low Priority / Documentation Gaps

### 12. create_rubric_score_distribution_chart() May Compare None Scores
**Location:** Lines ~1050-1070 (score color computation)
**Issue:** If `cross_judge_score` becomes None for categorical, comparisons will break

**Fix:** Add None check:
```python
colors = []
for score in scores:
    if score is None:
        colors.append('gray')  # Or skip this rubric
    elif score >= 0.7:
        colors.append('green')
    elif score >= 0.4:
        colors.append('orange')
    else:
        colors.append('red')
```

### 13. Chart Docstrings Say "self-contained"
**Location:** Various chart methods
**Issue:** Since Plotly is CDN-hosted, "self-contained" wording is slightly inaccurate

**Fix:** Update docstrings to say "CDN-hosted Plotly" instead of "self-contained"

### 14. render_template() May Need Custom Filters
**Location:** Lines ~900-950 (render_template method)
**Issue:** Template plan references formatting helpers; builder doesn't register custom Jinja filters

**Status:** May not be needed if template uses built-in filters. Check template requirements.

## Architectural Suggestions (Not Gaps)

### 15. Large File - Consider Splitting
**Issue:** report_builder.py is 782 lines and growing

**Suggestion:** Split into:
- `report_builder.py` - Main orchestration
- `chart_generator.py` - All chart methods
- `artifact_loader.py` - Loading and validation
- `view_model_builder.py` - View model construction

**Status:** Optional refactoring for maintainability

## Summary

**Critical (Must Fix):** 6 gaps (#1-6)
**Medium Priority:** 6 gaps (#7-12)
**Low Priority:** 2 gaps (#13-14)
**Architectural:** 1 suggestion (#15)

**Recommendation:** Fix critical gaps first (especially #1-4 which will cause immediate runtime errors), then address medium priority gaps for completeness.
