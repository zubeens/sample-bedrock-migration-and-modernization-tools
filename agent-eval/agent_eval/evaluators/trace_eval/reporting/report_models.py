"""
Data models for HTML report generation.

This module defines all dataclasses used to structure data for HTML report rendering.
The ReportViewModel is the top-level model passed to the Jinja2 template.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class RunSummary:
    """High-level run metadata extracted from normalized_run.metadata."""
    run_id: str
    processed_at: Optional[datetime]
    source: Optional[str]
    adapter_version: str
    segmentation_strategy: str
    run_confidence: float
    overall_mapping_coverage: float


@dataclass
class TraceSummary:
    """Trace-level statistics from trace_eval.deterministic_metrics."""
    turn_count: int
    total_steps: int
    tool_call_count: int
    avg_latency_ms: Optional[float]
    total_latency_ms: Optional[float]
    finish_reasons: Dict[str, int]  # histogram of finish reasons


@dataclass
class CategoricalSummary:
    """Summary for categorical rubric results."""
    aggregated_label: Optional[str]  # Final aggregated categorical label (None if aggregation failed)
    vote_breakdown: Dict[str, int]  # label -> count of judges who voted for it
    disagreement_text: str  # Human-readable disagreement description (e.g., "unanimous", "2-1 split")


@dataclass
class RubricScore:
    """Per-rubric aggregated score from trace_eval.rubric_results."""
    rubric_id: str
    scope: str  # "run" or "turn"
    turn_id: Optional[str]
    cross_judge_score: Optional[float]  # weighted_vote or weighted_average (None for categorical)
    disagreement_signal: Optional[float]  # May be None for categorical rubrics without numeric disagreement
    high_risk_flag: bool
    judge_count: int
    scoring_type: str  # "numeric" or "categorical"
    is_categorical: bool = False  # True for categorical rubrics
    categorical_summary: Optional[CategoricalSummary] = None  # Present only for categorical rubrics


@dataclass
class JudgeDetail:
    """Per-judge execution statistics aggregated from judge_runs.jsonl."""
    judge_id: str
    provider: str
    model: str
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    avg_latency_ms: Optional[float]


@dataclass
class LatencyStats:
    """Turn-level latency statistics from normalized_run.turns."""
    turn_id: str
    normalized_latency_ms: Optional[float]
    runtime_reported_latency_ms: Optional[float]
    total_latency_ms: Optional[float]
    step_count: int


@dataclass
class ToolActivity:
    """Tool usage per turn from normalized_run.turns."""
    turn_id: str
    tool_calls: List[Dict[str, Any]]  # List of tool call details (name, status, latency_ms)
    tool_call_count: int
    successful_tools: int
    failed_tools: int


@dataclass
class AdapterDiagnostics:
    """Adapter processing diagnostics from normalized_run.adapter_stats."""
    total_events_processed: int
    events_with_valid_timestamps: int
    dropped_events_count: int
    invalid_events_count: int
    confidence_penalties: List[Dict[str, Any]]  # List of {reason, penalty, location}
    orphan_tool_results: List[Dict[str, Any]]  # List of orphaned tool results
    warnings: List[str]  # List of warning messages
    missing_fields_summary: Dict[str, List[str]]  # Field name -> list of locations
    is_available: bool = True  # False when adapter_stats is completely missing


@dataclass
class EvidenceSpan:
    """
    Resolved evidence content from a selector.
    
    Represents a single piece of evidence extracted from the normalized run
    using a rubric selector, with full context for precise rendering and debugging.
    """
    selector: str  # The selector expression (e.g., "turns[*].steps[*].content")
    resolved_content: str  # The actual content extracted
    context_type: str  # "run" or "turn" - indicates scope of evidence
    turn_id: Optional[str] = None  # Present if context_type is "turn"
    source_location: Optional[str] = None  # Path to source field (e.g., "turns[0].steps[1].content")
    field_name: Optional[str] = None  # Field name extracted (e.g., "content", "tool_name")


@dataclass
class RubricEvidenceDetail:
    """
    Evidence and reasoning for a specific rubric evaluation.
    
    Contains all evidence spans resolved from selectors and the fields used
    for this rubric's evaluation. Includes resolution status for diagnostics.
    """
    rubric_id: str
    scope: str  # "run" or "turn"
    turn_id: Optional[str]  # Present if scope is "turn"
    evidence_spans: List[EvidenceSpan]  # Resolved evidence from selectors
    evidence_fields_used: List[str]  # List of field names from rubric selectors
    resolution_status: str = "success"  # "success", "selectors_missing", "resolution_failed", "partial"


@dataclass
class JudgeReasoningSnippet:
    """
    Per-judge reasoning for a rubric evaluation.
    
    Contains the judge's score and reasoning, with a preview for display.
    Properly typed for both numeric and categorical rubrics.
    
    Note: Exactly one of score_numeric or score_label should be populated.
    This is enforced by the builder, not the dataclass itself.
    """
    judge_id: str
    score_numeric: Optional[float]  # Present for numeric rubrics (mutually exclusive with score_label)
    score_label: Optional[str]  # Present for categorical rubrics (mutually exclusive with score_numeric)
    reasoning: str  # Full reasoning text
    reasoning_preview: str  # Truncated to max 200 chars for display


@dataclass
class DiagnosticWarning:
    """
    Diagnostic warning message with context (Gap #2).
    
    Used to report non-fatal issues during report generation.
    """
    level: str  # "warning", "error", "info"
    message: str
    location: Optional[str]  # Optional location context (e.g., "rubric_id:turn_id")


@dataclass
class ArtifactPaths:
    """
    Paths to canonical artifacts with checksums.
    
    Provides file paths and integrity checksums for all artifacts used
    in report generation. results and report are optional since they may
    not exist at certain stages.
    """
    normalized_run: str
    trace_eval: str
    judge_runs: str
    results: Optional[str] = None  # Optional - may not exist
    report: Optional[str] = None  # Optional - doesn't exist before write
    checksums: Dict[str, str] = field(default_factory=dict)  # filename -> SHA256 checksum


@dataclass
class ReportMetadata:
    """
    Report generation metadata and versioning (Gap #4).
    
    Tracks when and how the report was generated, including versions
    of source artifacts and generation tools.
    """
    generator_version: str  # Version of report generator
    generation_timestamp: datetime  # When report was generated
    source_artifact_versions: Dict[str, str]  # artifact_name -> version
    charts_enabled: bool  # Whether charts are present in the report (True only if at least one chart was successfully generated)
    template_version: str  # Version of template used


@dataclass
class ReportViewModel:
    """
    Complete view model for HTML template rendering.
    
    This is the top-level data structure passed to the Jinja2 template.
    Contains all data needed to render the complete HTML report.
    """
    run_summary: RunSummary
    trace_summary: TraceSummary
    rubric_scores: List[RubricScore]
    judge_details: List[JudgeDetail]
    latency_stats: List[LatencyStats]
    tool_activity: List[ToolActivity]
    adapter_diagnostics: AdapterDiagnostics
    artifact_paths: ArtifactPaths
    report_metadata: ReportMetadata
    evidence_details: List[RubricEvidenceDetail] = field(default_factory=list)
    # Key format: "rubric_id" for run-scoped, "rubric_id:turn_id" for turn-scoped
    judge_reasoning: Dict[str, List[JudgeReasoningSnippet]] = field(default_factory=dict)
    diagnostic_warnings: List[DiagnosticWarning] = field(default_factory=list)


# Helper functions for datetime parsing and serialization

def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """
    Parse datetime string from artifacts.
    
    Handles multiple datetime formats commonly found in artifacts.
    Returns None if parsing fails or input is None.
    
    Note: python-dateutil is an optional dependency. If not available,
    only ISO format parsing is supported.
    
    Args:
        dt_str: Datetime string in ISO format or similar
        
    Returns:
        Parsed datetime object or None
    """
    if not dt_str:
        return None
    
    try:
        # Try ISO format first (most common)
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        pass
    
    try:
        # Try common formats using dateutil if available
        from dateutil import parser
        return parser.parse(dt_str)
    except (ImportError, ValueError, AttributeError):
        pass
    
    return None


def serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Serialize datetime to ISO format string.
    
    Args:
        dt: Datetime object to serialize
        
    Returns:
        ISO format string or None
    """
    if dt is None:
        return None
    return dt.isoformat()


def format_datetime_display(dt: Optional[datetime]) -> str:
    """
    Format datetime for human-readable display in report.
    
    Handles timezone-aware and naive datetimes correctly.
    Only appends timezone info if the datetime is timezone-aware.
    
    Args:
        dt: Datetime object to format
        
    Returns:
        Formatted string like "2024-01-15 14:30:45 UTC" or "2024-01-15 14:30:45" or "N/A"
    """
    if dt is None:
        return "N/A"
    
    # Format base datetime
    base_format = dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Only append timezone if datetime is timezone-aware
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        # Get timezone name
        tz_name = dt.tzname() or "UTC"
        return f"{base_format} {tz_name}"
    
    return base_format
