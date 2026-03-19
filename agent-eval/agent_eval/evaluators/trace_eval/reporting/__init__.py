"""
HTML Report Generation Package.

This package provides functionality to generate self-contained HTML reports
from TraceEvaluator canonical artifacts (normalized_run.json, trace_eval.json,
judge_runs.jsonl, results.json).

Main entry point:
    generate_report() - Generate HTML report from artifacts

Key modules:
    report_models - Data models for report view
    report_builder - Core report building logic
    html_report - Public API for report generation
"""

# Public API
from .html_report import generate_report
from .report_builder import ReportGenerationError

__all__ = [
    'generate_report',
    'ReportGenerationError',
]
