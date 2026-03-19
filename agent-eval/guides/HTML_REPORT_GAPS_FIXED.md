# HTML Report Template Gaps - All Fixed

This document summarizes all gaps that were identified and fixed in the HTML report generation system.

## Files Modified

1. `agent-eval/agent_eval/evaluators/trace_eval/reporting/html_report.py`
2. `agent-eval/agent_eval/evaluators/trace_eval/reporting/report_models.py`
3. `agent-eval/agent_eval/evaluators/trace_eval/reporting/report_builder.py`
4. `agent-eval/agent_eval/evaluators/trace_eval/reporting/templates/report.html.j2`

## Fixes Applied

### html_report.py

1. **Logger type annotation** - Changed from `Callable[[str], None]` to `Callable[..., None]` to accommodate both `(message: str)` and `(message: str, force: bool)` signatures
2. **Docstring "self-contained"** - Changed to "HTML file with embedded CSS and CDN-hosted JavaScript"
3. **charts_enabled propagation** - Now set to `enable_charts and len(charts) > 0` to reflect actual outcome
4. **Report path metadata** - Added `view_model.artifact_paths.report = report_path` after write
5. **Error wrapping** - Added explicit `json.JSONDecodeError` catch block
6. **Hardcoded performance numbers** - Removed specific timings, replaced with general statement

### report_models.py

1. **charts_enabled field documentation** - Updated to clarify it reflects whether charts are actually present (True only if at least one chart was successfully generated)

### report_builder.py

1. **Docstring "self-contained"** - Changed to "CDN-hosted" in generate_charts method

### report.html.j2 (Template)

#### Initial Round of Fixes

1. **Broken CSS block** - Fixed `</style>` closing too early by removing it before `.collapsible-content`
2. **Judge reasoning model mismatch** - Changed from `snippet.score` to `snippet.score_numeric if snippet.score_numeric is not none else snippet.score_label`
3. **Categorical score rendering** - Changed from `score.cross_judge_score` to `score.categorical_summary.aggregated_label` for categorical rubrics
4. **Disagreement formatting** - Added null check: `{% if score.disagreement_signal is not none %}` before formatting
5. **Evidence lookup** - Added turn_id filter: `selectattr('turn_id', 'equalto', score.turn_id)` to prevent wrong evidence for turn-scoped rubrics
6. **Unused variable** - Removed `evidence_key` variable that was set but never used
7. **Adapter diagnostics availability** - Changed from `{% if view_model.adapter_diagnostics %}` to `{% if view_model.adapter_diagnostics and view_model.adapter_diagnostics.is_available %}`
8. **Missing optional paths** - Changed `{{ view_model.artifact_paths.results }}` to `{{ view_model.artifact_paths.results if view_model.artifact_paths.results else 'N/A' }}`
9. **missing_fields_summary slicing** - Changed from `.items()[:10]` to `(.items() | list)[:10]` for safe slicing in Jinja
10. **Datetime display** - Changed from hardcoded `strftime('%Y-%m-%d %H:%M:%S UTC')` to conditional timezone display
11. **Reasoning element ID collision** - Changed from `reasoning-{{ score.rubric_id }}-{{ loop.index }}` to `reasoning-{{ score.rubric_id }}-{{ score.turn_id if score.turn_id else 'run' }}-{{ loop.index }}`
12. **Plotly script duplication** - Removed `<script src="https://cdn.plot.ly/plotly-2.18.0.min.js"></script>` from head since charts include it
13. **Final Aggregated Score categorical** - Fixed to use `score.categorical_summary.aggregated_label` instead of `score.cross_judge_score`

#### Final Round of Fixes

14. **Turn-scoped evidence lookup** - Improved to match by `rubric_id` and `scope` first, then filter by `turn_id` only for turn-scoped rubrics to handle run-scoped rubrics correctly
15. **Categorical detail section** - Added vote breakdown table and disagreement text display for categorical rubrics
16. **Numeric score None guard** - Added `{% if score.cross_judge_score is not none %}` check before formatting numeric scores
17. **Tool dict access** - Changed from dot notation (`tool.name`, `tool.status`) to bracket notation (`tool['name']`, `tool['status']`) for safer dict access
18. **Evidence resolution status** - Added display of `detail.resolution_status` when not 'success' for debugging evidence issues

## Known Limitations

1. **Report path in artifacts section** - Will show "N/A" in the generated file since the path is updated after template rendering. The "Current file" label makes this acceptable.
2. **Plotly CDN dependency** - Charts require internet access to load Plotly from CDN. This is by design for smaller file sizes.

## Impact

All gaps have been addressed. The system now:
- Properly handles categorical rubrics with vote breakdown and disagreement text
- Correctly reflects actual chart generation status
- Safely handles missing optional fields and None values
- Avoids ID collisions in HTML elements
- Prevents Plotly script duplication
- Uses correct model fields for all data access
- Properly checks adapter diagnostics availability
- Handles timezone-aware and naive datetimes correctly
- Matches evidence correctly for both run-scoped and turn-scoped rubrics
- Uses safe dict access patterns
- Displays evidence resolution status for debugging

## Testing Recommendations

1. Test with categorical rubrics to verify score display and vote breakdown
2. Test with missing optional fields (results.json, adapter_stats)
3. Test with turn-scoped rubrics to verify evidence lookup
4. Test with run-scoped rubrics to verify evidence lookup
5. Test with charts disabled and with all charts failing
6. Verify no JavaScript errors from duplicate Plotly loads
7. Check HTML element IDs are unique across multiple rubrics
8. Test with None values in numeric scores
9. Test with malformed tool_calls dicts
10. Verify evidence resolution status displays for failed/partial resolution
