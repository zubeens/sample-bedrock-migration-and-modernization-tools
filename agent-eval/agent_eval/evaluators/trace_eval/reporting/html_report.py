"""
Public API for HTML report generation.

This module provides the main entry point for generating HTML reports
from TraceEvaluator canonical artifacts.
"""

from pathlib import Path
from typing import Optional, Callable, Any
import json

from .report_builder import ReportBuilder, ReportGenerationError


def generate_report(
    output_dir: str,
    run_id: str,
    enable_charts: bool = True,
    logger: Optional[Callable[..., None]] = None
) -> str:
    """
    Generate HTML report from canonical artifacts.
    
    This is the main public API for report generation. It loads artifacts
    from the output directory, builds a view model, generates charts (if enabled),
    renders the HTML template, and writes the report file.
    
    The generated report is an HTML file with embedded CSS and CDN-hosted JavaScript.
    Charts use CDN-hosted Plotly for interactivity. The report includes:
    
    - Run summary with metadata and confidence scores
    - Trace statistics (turn counts, tool usage, latency)
    - Rubric scores table with color coding and high-risk highlighting
    - Evidence display with per-rubric reasoning and judge details
    - Judge execution statistics and performance metrics
    - Latency analysis per turn
    - Tool activity tracking
    - Adapter diagnostics with confidence penalties and warnings
    - Interactive Plotly charts (if enabled):
      * Rubric score distribution
      * Judge disagreement analysis
      * Latency by turn
      * Tool activity by turn
      * Confidence penalty summary
    
    Args:
        output_dir: Directory containing canonical artifacts. Must contain:
                   - normalized_run.<run_id>.json (required)
                   - trace_eval.json (required)
                   - judge_runs.jsonl (required)
                   - results.json (optional, used for checksums)
        run_id: Run identifier for filename generation. Special characters will be
               sanitized to create a safe filename: report_<sanitized_run_id>.html
        enable_charts: Whether to generate Plotly charts (default: True).
                      Set to False for faster generation without visualizations.
                      Charts require internet access to load Plotly from CDN.
        logger: Optional logging function compatible with TraceEvaluator._log style.
               Should accept (message: str) or (message: str, force: bool).
               Type hint uses Callable[..., None] to accommodate both signatures.
               If not provided, uses module logger (logging.getLogger(__name__)).
               Used for warnings about missing optional data and chart generation.
        
    Returns:
        Path to generated HTML report file (str). The file will be named
        report_<sanitized_run_id>.html and located in output_dir.
        
    Raises:
        ReportGenerationError: If report generation fails due to:
            - Missing required artifacts (normalized_run, trace_eval, judge_runs)
            - Invalid JSON in artifacts
            - Template rendering errors
            - File write failures
            - Invalid output directory
            
    Performance:
        Performance varies based on trace size and system resources.
        Typical runs complete in under 1 second. Large traces may take longer.
        Memory usage scales linearly with trace size.
        
    Notes:
        - Report generation is non-fatal in the TraceEvaluator pipeline
        - Missing optional fields (latency, adapter_stats) are handled gracefully
        - Categorical rubrics are displayed separately from numeric charts
        - File write is atomic to prevent partial/corrupted reports
        - The report is viewable in any modern web browser
        
    Example:
        Basic usage with all defaults:
        
        >>> from agent_eval.evaluators.trace_eval.reporting import generate_report
        >>> report_path = generate_report(
        ...     output_dir="./eval_outputs/run_001",
        ...     run_id="test_run_001"
        ... )
        >>> print(f"Report generated: {report_path}")
        
        Generate report without charts (faster):
        
        >>> report_path = generate_report(
        ...     output_dir="./output",
        ...     run_id="my_run",
        ...     enable_charts=False
        ... )
        
        Use custom logger:
        
        >>> def my_logger(msg, force=False):
        ...     print(f"[REPORT] {msg}")
        >>> report_path = generate_report(
        ...     output_dir="./output",
        ...     run_id="my_run",
        ...     logger=my_logger
        ... )
    """
    try:
        # Instantiate ReportBuilder
        builder = ReportBuilder(
            output_dir=Path(output_dir),
            run_id=run_id,
            logger_func=logger
        )
        
        # Load artifacts
        artifacts = builder.load_artifacts()
        
        # Build view model
        view_model = builder.build_view_model(artifacts)
        
        # Generate charts if enabled
        charts = []
        if enable_charts:
            charts = builder.generate_charts(view_model)
        
        # Update charts_enabled in metadata to reflect actual outcome
        # True only if charts were requested AND at least one chart was generated
        view_model.report_metadata.charts_enabled = enable_charts and len(charts) > 0
        
        # Set report path before rendering so template can display it
        from agent_eval.evaluators.trace_eval.reporting.report_builder import sanitize_filename
        safe_run_id = sanitize_filename(run_id)
        report_path = Path(output_dir) / f"report_{safe_run_id}.html"
        view_model.artifact_paths.report = str(report_path)
        
        # Render template
        html_content = builder.render_template(view_model, charts)
        
        # Write report atomically
        actual_report_path = builder.write_report_atomic(html_content)
        
        return actual_report_path
    
    except ReportGenerationError:
        # Re-raise ReportGenerationError as-is
        raise
    
    except json.JSONDecodeError as e:
        # Wrap JSON parsing errors with clear messaging
        raise ReportGenerationError(
            f"Invalid JSON in artifact file: {e}"
        ) from e
    
    except (FileNotFoundError, ValueError, IOError) as e:
        # Wrap file system and validation errors in ReportGenerationError
        raise ReportGenerationError(
            f"Report generation failed: {e}"
        ) from e
    
    except Exception as e:
        # Wrap any other unexpected errors
        raise ReportGenerationError(
            f"Unexpected error during report generation: {e}"
        ) from e


__all__ = ['generate_report', 'ReportGenerationError']
