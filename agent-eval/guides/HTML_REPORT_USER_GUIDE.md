# HTML Report Generation User Guide

## Overview

The HTML Report Generation feature provides comprehensive, interactive visualization of agent evaluation results. After the TraceEvaluator completes an evaluation run, it automatically generates a self-contained HTML report with embedded charts, collapsible sections, and detailed diagnostics.

## Quick Start

### Automatic Generation

Reports are generated automatically after evaluation completes:

```bash
python -m agent_eval.cli \
  --input trace.json \
  --judge-config judges.yaml \
  --rubrics rubrics.yaml \
  --output-dir ./output
```

The report will be saved as `output/report_<run_id>.html`.

### Skip Report Generation

To disable automatic report generation:

```bash
python -m agent_eval.cli \
  --input trace.json \
  --judge-config judges.yaml \
  --rubrics rubrics.yaml \
  --output-dir ./output \
  --skip-report
```

### Standalone Report Generation

Generate reports from existing evaluation artifacts:

```python
from agent_eval.evaluators.trace_eval.reporting import generate_report

# Generate report with charts (default)
report_path = generate_report(
    output_dir="./output",
    run_id="my_run",
    enable_charts=True
)
print(f"Report generated: {report_path}")
```

### Generate Without Charts

For faster generation without visualizations:

```python
report_path = generate_report(
    output_dir="./output",
    run_id="my_run",
    enable_charts=False
)
```

## Report Structure

The generated HTML report contains the following sections:

### 1. Report Metadata

- Generator version and timestamp
- Source artifact versions
- Charts enabled status
- Template version

### 2. Run Summary

High-level evaluation context:
- Run ID
- Processing timestamp
- Source system identifier
- Adapter version
- Segmentation strategy
- Run confidence score (color-coded)
- Overall mapping coverage percentage

### 3. Trace Summary

Execution statistics:
- Turn count
- Total steps
- Tool call count
- Average latency (if available)
- Total latency (if available)
- Finish reasons histogram

### 4. Rubric Scores Table

Sortable table with:
- Rubric ID
- Scope (run/turn)
- Turn ID (for turn-scoped rubrics)
- Cross-judge score (color-coded)
- Disagreement signal
- High-risk flag indicator
- Scoring type (numeric/categorical)

**Color Coding:**
- Green: Score ≥ 0.7 (high quality)
- Yellow/Orange: Score ≥ 0.4 (medium quality)
- Red: Score < 0.4 (low quality)

**High-Risk Highlighting:**
- Rows with high-risk flag are highlighted with red background and border

### 5. Evidence Display

For each rubric, collapsible "Why this score?" sections show:
- Final aggregated score or label
- Evidence fields used (from rubric selectors)
- Evidence previews (resolved content from trace)
- Per-judge reasoning snippets
- Disagreement summary (if disagreement signal exceeds threshold)

**Evidence Sources:**
- Rubric selectors (JSONPath expressions)
- Normalized trace fields
- Persisted judge reasoning from judge_runs.jsonl

### 6. Judge Details Table

Per-judge execution statistics:
- Judge ID
- Provider (e.g., bedrock, openai)
- Model ID
- Total jobs executed
- Success rate (with visual progress bar)
- Average latency

### 7. Latency Analysis

Per-turn latency breakdown:
- Turn ID
- Normalized latency (ms)
- Runtime-reported latency (ms)
- Total latency (ms)
- Step count

### 8. Tool Activity

Per-turn tool usage tracking:
- Turn ID
- Tool call count
- Successful tool calls
- Failed tool calls
- Individual tool call details (name, status, latency)

### 9. Adapter Diagnostics

Collapsible section with processing details:
- Total events processed
- Events with valid timestamps
- Dropped events count
- Invalid events count
- Confidence penalties table (reason, penalty, location)
- Orphan tool results
- Warnings list
- Missing fields summary (top 10 most common)

### 10. Artifact References

File paths and checksums for canonical artifacts:
- normalized_run.<run_id>.json
- trace_eval.json
- judge_runs.jsonl
- results.json
- report_<run_id>.html

### 11. Interactive Charts

When `enable_charts=True`, the report includes Plotly visualizations:

1. **Rubric Score Distribution** (bar chart)
   - Shows score distribution across numeric rubrics
   - Color-coded by score threshold
   - Categorical rubrics excluded

2. **Judge Disagreement Analysis** (scatter plot)
   - Plots disagreement signal per rubric
   - High-risk threshold line at 0.3
   - Color-coded by high-risk flag

3. **Latency by Turn** (line chart)
   - Shows total latency trend across turns
   - Helps identify performance bottlenecks

4. **Tool Activity by Turn** (stacked bar chart)
   - Successful vs failed tool calls per turn
   - Green for successful, red for failed

5. **Confidence Penalty Summary** (horizontal bar chart)
   - Aggregated penalties by reason
   - Helps identify data quality issues

## API Reference

### generate_report()

```python
def generate_report(
    output_dir: str,
    run_id: str,
    enable_charts: bool = True,
    logger: Optional[Callable[[str], None]] = None
) -> str
```

**Parameters:**

- `output_dir` (str): Directory containing canonical artifacts
  - Must contain: `normalized_run.<run_id>.json`, `trace_eval.json`, `judge_runs.jsonl`
  - Optional: `results.json` (used for checksums)

- `run_id` (str): Run identifier for filename generation
  - Special characters are sanitized for safe filenames
  - Output filename: `report_<sanitized_run_id>.html`

- `enable_charts` (bool, default=True): Whether to generate Plotly charts
  - Set to `False` for faster generation without visualizations
  - Charts require internet access to load Plotly from CDN

- `logger` (Optional[Callable], default=None): Custom logging function
  - Should accept `(message: str)` or `(message: str, force: bool)`
  - If not provided, uses module logger

**Returns:**

- `str`: Path to generated HTML report file

**Raises:**

- `ReportGenerationError`: If report generation fails due to:
  - Missing required artifacts
  - Invalid JSON in artifacts
  - Template rendering errors
  - File write failures

**Example:**

```python
from agent_eval.evaluators.trace_eval.reporting import generate_report

# Basic usage
report_path = generate_report(
    output_dir="./output",
    run_id="test_run_001"
)

# Without charts
report_path = generate_report(
    output_dir="./output",
    run_id="test_run_001",
    enable_charts=False
)

# With custom logger
def my_logger(msg, force=False):
    print(f"[REPORT] {msg}")

report_path = generate_report(
    output_dir="./output",
    run_id="test_run_001",
    logger=my_logger
)
```

## Performance

Report generation is fast and scales well:

| Run Size | Turns | Rubrics | Judges | Generation Time |
|----------|-------|---------|--------|-----------------|
| Typical  | 10    | 5       | 3      | ~0.2s           |
| Large    | 100   | 10      | 5      | ~1-2s           |

**Performance Characteristics:**
- Memory usage scales linearly with trace size
- Chart generation adds ~0.1-0.3s overhead
- Template rendering is cached for efficiency
- Atomic file write prevents partial reports

See [HTML_REPORT_PERFORMANCE.md](HTML_REPORT_PERFORMANCE.md) for detailed benchmarks.

## Troubleshooting

### Report Not Generated

**Symptoms:** No report file in output directory

**Solutions:**
1. Check if `--skip-report` flag was used
2. Verify all required artifacts exist:
   - `normalized_run.<run_id>.json`
   - `trace_eval.json`
   - `judge_runs.jsonl`
3. Check evaluation logs for report generation warnings
4. Verify output directory is writable

### Missing Charts

**Symptoms:** Report displays but charts are empty or missing

**Solutions:**
1. Ensure `enable_charts=True` (default)
2. Check browser has internet access for Plotly CDN
3. Open browser console to check for JavaScript errors
4. Verify trace contains data for charts (rubrics, latency, tools)

### Empty Sections

**Symptoms:** Some report sections show "unavailable" or "N/A"

**Solutions:**
1. Verify artifacts contain expected data:
   - Rubrics: Check `trace_eval.json` has `rubric_results`
   - Judges: Check `judge_runs.jsonl` is not empty
   - Latency: Check turns have latency fields
   - Adapter diagnostics: Check `normalized_run.json` has `adapter_stats`
2. This is expected behavior for optional data - report handles gracefully

### File Not Found Error

**Symptoms:** `FileNotFoundError` or `ReportGenerationError`

**Solutions:**
1. Verify run_id matches the normalized_run filename
2. Check all required artifacts are present
3. Ensure output_dir path is correct
4. Verify file permissions allow reading artifacts

### Template Rendering Error

**Symptoms:** `jinja2.TemplateError` or template-related errors

**Solutions:**
1. Check run_id doesn't contain invalid characters
2. Verify Jinja2 is installed: `pip install jinja2>=3.1.0`
3. Check template file exists: `agent_eval/evaluators/trace_eval/reporting/templates/report.html.j2`
4. Verify no data corruption in artifacts

### Charts Not Interactive

**Symptoms:** Charts display but don't respond to mouse interactions

**Solutions:**
1. Ensure browser has internet access for Plotly CDN
2. Check browser console for JavaScript errors
3. Try different browser (Chrome, Firefox, Safari)
4. Verify Plotly CDN is accessible: https://cdn.plot.ly/plotly-latest.min.js

### Performance Issues

**Symptoms:** Report generation takes longer than expected

**Solutions:**
1. Disable charts for faster generation: `enable_charts=False`
2. Check trace size - very large traces (1000+ turns) may be slower
3. Verify sufficient disk space for report file
4. Check system resources (CPU, memory)

## Advanced Usage

### Custom Logger Integration

Integrate with existing logging infrastructure:

```python
import logging
from agent_eval.evaluators.trace_eval.reporting import generate_report

# Use standard Python logger
logger = logging.getLogger(__name__)

def log_wrapper(msg, force=False):
    if force:
        logger.info(msg)
    else:
        logger.debug(msg)

report_path = generate_report(
    output_dir="./output",
    run_id="my_run",
    logger=log_wrapper
)
```

### Batch Report Generation

Generate reports for multiple evaluation runs:

```python
from pathlib import Path
from agent_eval.evaluators.trace_eval.reporting import generate_report

output_dirs = [
    "./output/run_001",
    "./output/run_002",
    "./output/run_003"
]

for output_dir in output_dirs:
    run_id = Path(output_dir).name
    try:
        report_path = generate_report(
            output_dir=output_dir,
            run_id=run_id
        )
        print(f"✓ Generated: {report_path}")
    except Exception as e:
        print(f"✗ Failed {run_id}: {e}")
```

### Error Handling

Robust error handling for production use:

```python
from agent_eval.evaluators.trace_eval.reporting import (
    generate_report,
    ReportGenerationError
)

try:
    report_path = generate_report(
        output_dir="./output",
        run_id="my_run"
    )
    print(f"Report generated: {report_path}")
    
except ReportGenerationError as e:
    print(f"Report generation failed: {e}")
    # Handle gracefully - evaluation artifacts still valid
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Log and investigate
```

## Security Considerations

The report generator implements several security measures:

1. **Path Sanitization**: Run IDs are sanitized to prevent directory traversal attacks
2. **XSS Prevention**: Jinja2 autoescape is enabled to prevent cross-site scripting
3. **Safe JSON Embedding**: Uses Jinja2's `tojson` filter for safe JavaScript embedding
4. **No Credential Exposure**: Reports never include credentials or API keys
5. **Atomic Writes**: Prevents partial/corrupted report files

## Browser Compatibility

The generated HTML reports are compatible with:

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Requirements:**
- JavaScript enabled
- Internet access for Plotly CDN (charts only)
- Modern CSS support (flexbox, grid)

## Related Documentation

- [HTML_REPORT_PERFORMANCE.md](HTML_REPORT_PERFORMANCE.md) - Performance benchmarks and optimization
- [HTML_REPORT_TESTING_QUICK_REFERENCE.md](HTML_REPORT_TESTING_QUICK_REFERENCE.md) - Testing guidance
- [HTML_REPORT_EXPECTED_BEHAVIORS.md](HTML_REPORT_EXPECTED_BEHAVIORS.md) - Expected behavior specifications
- [MANUAL_TESTING_GUIDE.md](MANUAL_TESTING_GUIDE.md) - Manual testing procedures
- [SECURITY_TESTING_SUMMARY.md](SECURITY_TESTING_SUMMARY.md) - Security testing results

## Support

For issues or questions:

1. Check this guide's troubleshooting section
2. Review related documentation above
3. Check evaluation logs for warnings
4. Verify artifacts are valid and complete
5. Test with sample fixtures: `test-fixtures/baseline/`
