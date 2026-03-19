"""
Report builder for HTML report generation.

This module provides the ReportBuilder class which orchestrates the process
of loading canonical artifacts, building view models, generating charts,
and rendering HTML reports.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

# Module logger for fallback logging
logger = logging.getLogger(__name__)


class ReportGenerationError(Exception):
    """
    Custom exception raised when report generation fails.
    
    This exception is raised for fatal errors during report generation,
    such as missing required artifacts, invalid JSON, or file write failures.
    """
    pass


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe file system usage.
    
    Delegates to the shared filename_utils module, which is the canonical
    implementation. This wrapper is retained for backward compatibility
    with existing callers that import from report_builder.
    
    Args:
        filename: The filename string to sanitize
        
    Returns:
        Sanitized filename safe for file system use
        
    Examples:
        >>> sanitize_filename("test_run_001")
        'test_run_001'
        >>> sanitize_filename("test/run/../001")
        'test_run___001'
        >>> sanitize_filename("...test___")
        'test'
        >>> sanitize_filename("")
        'run'
    """
    from agent_eval.evaluators.trace_eval.filename_utils import sanitize_filename as _sanitize
    return _sanitize(filename)


class ReportBuilder:
    """
    Builder class for generating HTML reports from canonical artifacts.
    
    This class orchestrates the entire report generation process:
    1. Loading and validating canonical artifacts
    2. Building the view model from artifacts
    3. Generating Plotly charts (optional)
    4. Rendering the Jinja2 template
    5. Writing the final HTML report
    
    The builder is designed to be non-invasive and does not modify
    any canonical artifacts during report generation.
    
    Attributes:
        output_dir: Path to directory containing canonical artifacts
        run_id: Run identifier for filename generation
    """
    
    def __init__(self, output_dir: Path, run_id: str, logger_func: Optional[callable] = None):
        """
        Initialize the ReportBuilder.
        
        Args:
            output_dir: Path to directory containing canonical artifacts
                       (normalized_run.json, trace_eval.json, judge_runs.jsonl, results.json)
            run_id: Run identifier used for filename generation
                   (will be sanitized for safe file system usage)
            logger_func: Optional logging function compatible with TraceEvaluator._log style
                        (accepts message: str and optionally force: bool)
        
        Raises:
            ValueError: If output_dir does not exist or is not a directory
            ValueError: If run_id is empty
        """
        if not isinstance(output_dir, Path):
            output_dir = Path(output_dir)
        
        if not output_dir.exists():
            raise ValueError(f"Output directory does not exist: {output_dir}")
        
        if not output_dir.is_dir():
            raise ValueError(f"Output path is not a directory: {output_dir}")
        
        if not run_id or not run_id.strip():
            raise ValueError("run_id cannot be empty")
        
        self.output_dir = output_dir
        self.run_id = run_id.strip()
        self.safe_run_id = sanitize_filename(self.run_id)
        self.logger = logger_func if logger_func else self._default_logger
    
    def _default_logger(self, message: str, force: bool = False) -> None:
        """
        Default logger that uses module logger.
        
        Args:
            message: Message to log
            force: Ignored (for compatibility with TraceEvaluator._log)
        """
        logger.info(message)
    
    def validate_artifacts(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate loaded artifacts for required and preferred optional fields.
        
        This method validates the structure and content of loaded artifacts:
        - Checks for required fields (raises ReportGenerationError if missing)
        - Checks for preferred optional fields (logs warnings if missing, doesn't fail)
        - Verifies run_id consistency across artifacts
        
        Args:
            artifacts: Dictionary containing loaded artifacts with keys:
                      - normalized_run: Parsed normalized_run.json
                      - trace_eval: Parsed trace_eval.json
                      - judge_runs: List of parsed judge_runs.jsonl records
                      - results: Parsed results.json (may be None)
        
        Returns:
            The validated artifacts dictionary (same as input)
        
        Raises:
            ReportGenerationError: If required fields are missing or run_id is inconsistent
        """
        warnings = []
        
        # Validate normalized_run
        normalized_run = artifacts.get('normalized_run')
        if normalized_run is None:
            raise ReportGenerationError("Missing normalized_run artifact")
        
        # Required fields in normalized_run
        if 'run_id' not in normalized_run:
            raise ReportGenerationError("normalized_run missing required field: run_id")
        
        if 'turns' not in normalized_run:
            raise ReportGenerationError("normalized_run missing required field: turns")
        
        # Preferred optional fields in normalized_run
        if 'metadata' not in normalized_run:
            warnings.append("normalized_run missing preferred optional field: metadata")
        
        if 'adapter_stats' not in normalized_run:
            warnings.append("normalized_run missing preferred optional field: adapter_stats")
        
        # Validate trace_eval
        trace_eval = artifacts.get('trace_eval')
        if trace_eval is None:
            raise ReportGenerationError("Missing trace_eval artifact")
        
        # Required fields in trace_eval
        if 'deterministic_metrics' not in trace_eval:
            raise ReportGenerationError("trace_eval missing required field: deterministic_metrics")
        
        # Preferred optional fields in trace_eval
        if 'rubric_results' not in trace_eval:
            warnings.append("trace_eval missing preferred optional field: rubric_results (enables graceful partial rendering)")
        
        # Validate judge_runs
        judge_runs = artifacts.get('judge_runs')
        if judge_runs is None:
            raise ReportGenerationError("Missing judge_runs artifact")
        
        if not isinstance(judge_runs, list):
            raise ReportGenerationError("judge_runs must be a list")
        
        # Validate each judge_runs record
        for idx, record in enumerate(judge_runs):
            if not isinstance(record, dict):
                raise ReportGenerationError(f"judge_runs record {idx} is not a dictionary")
            
            # Required fields in each record
            if 'judge_id' not in record:
                raise ReportGenerationError(f"judge_runs record {idx} missing required field: judge_id")
            
            if 'status' not in record:
                raise ReportGenerationError(f"judge_runs record {idx} missing required field: status")
            
            # Preferred optional fields
            if 'job_id' not in record:
                warnings.append(f"judge_runs record {idx} missing preferred optional field: job_id (backward compatibility)")
        
        # Validate results.json (if present)
        results = artifacts.get('results')
        if results is not None:
            # Required-when-present fields
            if 'run_id' not in results:
                raise ReportGenerationError("results.json missing required-when-present field: run_id")
            
            # Optional fields (warn if missing)
            if 'artifact_checksums' not in results:
                warnings.append("results.json missing optional field: artifact_checksums")
            
            if 'artifact_paths' not in results:
                warnings.append("results.json missing optional field: artifact_paths")
            
            if 'summary' not in results:
                warnings.append("results.json missing optional field: summary")
        
        # Verify run_id consistency
        normalized_run_id = normalized_run.get('run_id')
        
        # Check consistency with results.json (if present)
        if results is not None and 'run_id' in results:
            results_run_id = results['run_id']
            if normalized_run_id != results_run_id:
                raise ReportGenerationError(
                    f"run_id inconsistency: normalized_run has '{normalized_run_id}' "
                    f"but results.json has '{results_run_id}'"
                )
        
        # Check consistency with trace_eval.run_id (optional - if absent, ignore; if present, verify; if inconsistent, warn only)
        if 'run_id' in trace_eval:
            trace_eval_run_id = trace_eval['run_id']
            if normalized_run_id != trace_eval_run_id:
                warnings.append(
                    f"run_id inconsistency (non-fatal): normalized_run has '{normalized_run_id}' "
                    f"but trace_eval has '{trace_eval_run_id}'"
                )
        
        # Log all warnings
        for warning in warnings:
            self.logger(f"⚠ Warning: {warning}")
        
        return artifacts
    def load_artifacts(self) -> Dict[str, Any]:
        """
        Load all canonical artifacts from output directory.

        This method loads the four canonical artifacts produced by TraceEvaluator:
        1. normalized_run.<run_id>.json - Normalized trace data
        2. trace_eval.json - Evaluation metrics and rubric results
        3. judge_runs.jsonl - Per-judge execution records (streaming)
        4. results.json - Summary and checksums (optional)

        The method uses streaming parsing for judge_runs.jsonl to avoid loading
        the entire file into memory. After loading, it calls validate_artifacts()
        to ensure data integrity.

        Returns:
            Dictionary with keys:
                - normalized_run: Parsed normalized_run.json
                - trace_eval: Parsed trace_eval.json
                - judge_runs: List of parsed judge_runs.jsonl records
                - results: Parsed results.json (may be None if file missing)

        Raises:
            FileNotFoundError: If any required artifact file is missing
            json.JSONDecodeError: If any artifact contains invalid JSON
            ReportGenerationError: If validation fails after loading
        """
        import json

        artifacts = {}

        # Load normalized_run with run_id in filename
        normalized_path = self.output_dir / f"normalized_run.{self.safe_run_id}.json"

        if not normalized_path.exists():
            raise FileNotFoundError(
                f"Missing normalized_run artifact: {normalized_path}\n"
                f"Expected file: normalized_run.{self.safe_run_id}.json"
            )

        try:
            with open(normalized_path, 'r', encoding='utf-8') as f:
                artifacts['normalized_run'] = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in normalized_run file: {normalized_path}",
                e.doc,
                e.pos
            )

        # Load trace_eval.json
        trace_eval_path = self.output_dir / "trace_eval.json"

        if not trace_eval_path.exists():
            raise FileNotFoundError(
                f"Missing trace_eval artifact: {trace_eval_path}\n"
                f"Expected file: trace_eval.json"
            )

        try:
            with open(trace_eval_path, 'r', encoding='utf-8') as f:
                artifacts['trace_eval'] = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in trace_eval file: {trace_eval_path}",
                e.doc,
                e.pos
            )

        # Load judge_runs.jsonl (line-by-line streaming)
        judge_runs_path = self.output_dir / "judge_runs.jsonl"

        if not judge_runs_path.exists():
            raise FileNotFoundError(
                f"Missing judge_runs artifact: {judge_runs_path}\n"
                f"Expected file: judge_runs.jsonl"
            )

        judge_runs = []
        try:
            with open(judge_runs_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        # Skip empty lines
                        continue
                    try:
                        record = json.loads(line)
                        judge_runs.append(record)
                    except json.JSONDecodeError as e:
                        raise json.JSONDecodeError(
                            f"Invalid JSON in judge_runs.jsonl at line {line_num}: {judge_runs_path}",
                            e.doc,
                            e.pos
                        )
        except json.JSONDecodeError:
            # Re-raise JSON errors from inner try block
            raise

        artifacts['judge_runs'] = judge_runs

        # Load results.json (optional, graceful if missing)
        results_path = self.output_dir / "results.json"

        if results_path.exists():
            try:
                with open(results_path, 'r', encoding='utf-8') as f:
                    artifacts['results'] = json.load(f)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"Invalid JSON in results file: {results_path}",
                    e.doc,
                    e.pos
                )
        else:
            # results.json is optional
            artifacts['results'] = None

        # Validate loaded artifacts before returning
        validated_artifacts = self.validate_artifacts(artifacts)

        return validated_artifacts

    def extract_checksums(self, artifacts: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract or compute checksums for canonical artifacts.

        This method implements a two-tier checksum strategy:
        1. First priority: Read checksums from results.json if present
        2. Fallback: Compute SHA256 checksums for all present canonical artifacts

        The precedence ensures that checksums from results.json (which are
        computed during the evaluation run) take priority over checksums
        computed during report generation.

        Args:
            artifacts: Dictionary containing loaded artifacts with keys:
                      - normalized_run, trace_eval, judge_runs, results

        Returns:
            Dictionary mapping artifact filename to SHA256 checksum hex string.
            Example: {
                "normalized_run.test_run_001.json": "abc123...",
                "trace_eval.json": "def456...",
                "judge_runs.jsonl": "ghi789...",
                "results.json": "jkl012..."
            }

        Notes:
            - If results.json is present and contains artifact_checksums, those
              checksums are used as-is
            - If results.json is missing or doesn't contain checksums, this method
              computes checksums for all present canonical artifacts
            - results.json is only included in computed checksums if it exists
            - Checksums are computed from the actual files on disk, not from
              the in-memory artifacts dictionary
        """
        import hashlib

        # First priority: Check if results.json has checksums
        results = artifacts.get('results')
        if results is not None and 'artifact_checksums' in results:
            checksums = results['artifact_checksums']
            if isinstance(checksums, dict) and checksums:
                self.logger("Using checksums from results.json")
                return checksums

        # Fallback: Compute checksums for all present canonical artifacts
        self.logger("Computing checksums for canonical artifacts")
        checksums = {}

        # Define canonical artifact filenames
        artifact_files = [
            f"normalized_run.{self.safe_run_id}.json",
            "trace_eval.json",
            "judge_runs.jsonl"
        ]

        # Include results.json only if it exists
        results_path = self.output_dir / "results.json"
        if results_path.exists():
            artifact_files.append("results.json")

        # Compute SHA256 checksum for each file
        for filename in artifact_files:
            file_path = self.output_dir / filename

            if not file_path.exists():
                # Skip files that don't exist (shouldn't happen for required artifacts)
                self.logger(f"⚠ Warning: Artifact file not found for checksum: {filename}")
                continue

            try:
                sha256_hash = hashlib.sha256()

                # Read file in chunks to handle large files efficiently
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        sha256_hash.update(chunk)

                checksums[filename] = sha256_hash.hexdigest()

            except IOError as e:
                self.logger(f"⚠ Warning: Failed to compute checksum for {filename}: {e}")
                continue

        return checksums



    def build_view_model(self, artifacts: Dict[str, Any]) -> 'ReportViewModel':
        """
        Build view model from loaded artifacts.
        
        This method extracts and transforms data from all canonical artifacts
        into a structured ReportViewModel ready for template rendering. It handles:
        - Run summary from normalized_run.metadata (with fallback to defaults)
        - Trace statistics from trace_eval.deterministic_metrics
        - Rubric scores from trace_eval.rubric_results (with categorical handling)
        - Judge details aggregated from judge_runs
        - Latency stats from normalized_run.turns
        - Tool activity from normalized_run.turns
        - Adapter diagnostics from normalized_run.adapter_stats (with graceful handling)
        - Evidence resolution and judge reasoning extraction
        - Artifact paths with checksums
        - Report metadata with versioning
        
        Args:
            artifacts: Dictionary containing all loaded artifacts with keys:
                      - normalized_run: Parsed normalized_run.json
                      - trace_eval: Parsed trace_eval.json
                      - judge_runs: List of parsed judge_runs.jsonl records
                      - results: Parsed results.json (may be None)
        
        Returns:
            Complete ReportViewModel instance ready for template rendering
        
        Raises:
            ReportGenerationError: If required fields are missing or data is invalid
        """
        from .report_models import (
            ReportViewModel, RunSummary, TraceSummary, RubricScore,
            JudgeDetail, LatencyStats, ToolActivity, AdapterDiagnostics,
            ArtifactPaths, ReportMetadata, EvidenceSpan, RubricEvidenceDetail,
            JudgeReasoningSnippet, DiagnosticWarning, CategoricalSummary,
            parse_datetime
        )
        from datetime import datetime
        
        normalized_run = artifacts['normalized_run']
        trace_eval = artifacts['trace_eval']
        judge_runs = artifacts['judge_runs']
        
        # Extract RunSummary from normalized_run.metadata
        metadata = normalized_run.get('metadata', {})
        
        # If metadata missing, build RunSummary from fallback fields with defaults
        if not metadata:
            self.logger("⚠ Warning: metadata missing from normalized_run, using fallback fields")
            run_summary = RunSummary(
                run_id=normalized_run.get('run_id', 'unknown'),
                processed_at=None,
                source=None,
                adapter_version='unknown',
                segmentation_strategy='unknown',
                run_confidence=0.0,
                overall_mapping_coverage=0.0
            )
        else:
            # Extract from metadata
            processed_at_str = metadata.get('processed_at')
            processed_at = parse_datetime(processed_at_str) if processed_at_str else None
            
            mapping_coverage = metadata.get('mapping_coverage', {})
            overall_coverage = mapping_coverage.get('overall_mapping_coverage', 0.0) if isinstance(mapping_coverage, dict) else 0.0
            
            run_summary = RunSummary(
                run_id=normalized_run.get('run_id', 'unknown'),
                processed_at=processed_at,
                source=metadata.get('source'),
                adapter_version=metadata.get('adapter_version', 'unknown'),
                segmentation_strategy=metadata.get('segmentation_strategy_used', 'unknown'),
                run_confidence=metadata.get('run_confidence', 0.0),
                overall_mapping_coverage=overall_coverage
            )
        
        # Extract TraceSummary from trace_eval.deterministic_metrics
        det_metrics = trace_eval.get('deterministic_metrics', {})
        
        trace_summary = TraceSummary(
            turn_count=det_metrics.get('turn_count', 0),
            total_steps=det_metrics.get('total_steps', 0),
            tool_call_count=det_metrics.get('tool_call_count', 0),
            avg_latency_ms=det_metrics.get('avg_latency_ms'),
            total_latency_ms=det_metrics.get('total_latency_ms'),
            finish_reasons=det_metrics.get('finish_reasons', {})
        )
        
        # Extract RubricScore list from trace_eval.rubric_results
        rubric_scores = []
        rubric_results = trace_eval.get('rubric_results', [])
        
        if not rubric_results:
            self.logger("⚠ Warning: No rubric_results in trace_eval")
        
        for rubric_result in rubric_results:
            cross_judge = rubric_result.get('cross_judge_result', {})
            scoring_type = cross_judge.get('scoring_type', 'numeric')
            is_categorical = (scoring_type == 'categorical')
            
            # Handle categorical vs numeric rubrics differently
            if is_categorical:
                # Build categorical summary
                within_judge_results = rubric_result.get('within_judge_results', [])
                vote_breakdown = {}
                for judge_result in within_judge_results:
                    label = str(judge_result.get('score', 'unknown'))
                    vote_breakdown[label] = vote_breakdown.get(label, 0) + 1
                
                # Determine aggregated label (most common vote)
                aggregated_label = None
                if vote_breakdown:
                    aggregated_label = max(vote_breakdown, key=vote_breakdown.get)
                
                # Generate disagreement text
                if not vote_breakdown:
                    disagreement_text = "No votes"
                elif len(vote_breakdown) == 1:
                    disagreement_text = "Unanimous"
                elif len(vote_breakdown) == 2:
                    counts = sorted(vote_breakdown.values(), reverse=True)
                    disagreement_text = f"{counts[0]}-{counts[1]} split"
                else:
                    disagreement_text = "High disagreement"
                
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
            
            rubric_scores.append(score)
        
        # Sort rubric scores by rubric_id (default sort order)
        rubric_scores.sort(key=lambda x: x.rubric_id)
        
        # Aggregate JudgeDetail list from judge_runs by judge_id
        if not judge_runs:
            self.logger("⚠ Warning: judge_runs is empty, no judge details available")
            judge_details = []
        else:
            judge_stats = {}
            
            for job in judge_runs:
                judge_id = job.get('judge_id', 'unknown')
                
                if judge_id not in judge_stats:
                    judge_stats[judge_id] = {
                        'provider': job.get('provider', 'unknown'),
                        'model': job.get('model', 'unknown'),
                        'total_jobs': 0,
                        'successful_jobs': 0,
                        'failed_jobs': 0,
                        'latencies': []
                    }
                
                stats = judge_stats[judge_id]
                stats['total_jobs'] += 1
                
                status = job.get('status', 'unknown')
                if status == 'success':
                    stats['successful_jobs'] += 1
                else:
                    stats['failed_jobs'] += 1
                
                # Collect latency if available
                latency = job.get('latency_ms')
                if latency is not None:
                    stats['latencies'].append(latency)
            
            # Build JudgeDetail list
            judge_details = []
            for judge_id, stats in judge_stats.items():
                # Calculate average latency
                avg_latency = None
                if stats['latencies']:
                    avg_latency = sum(stats['latencies']) / len(stats['latencies'])
                
                detail = JudgeDetail(
                    judge_id=judge_id,
                    provider=stats['provider'],
                    model=stats['model'],
                    total_jobs=stats['total_jobs'],
                    successful_jobs=stats['successful_jobs'],
                    failed_jobs=stats['failed_jobs'],
                    avg_latency_ms=avg_latency
                )
                judge_details.append(detail)
            
            # Sort judge details by judge_id (default sort order)
            judge_details.sort(key=lambda x: x.judge_id)
        
        # Extract LatencyStats list from normalized_run.turns
        latency_stats = []
        turns = normalized_run.get('turns', [])
        
        for turn in turns:
            turn_id = turn.get('turn_id', 'unknown')
            steps = turn.get('steps', [])
            
            stat = LatencyStats(
                turn_id=turn_id,
                normalized_latency_ms=turn.get('normalized_latency_ms'),
                runtime_reported_latency_ms=turn.get('runtime_reported_latency_ms'),
                total_latency_ms=turn.get('total_latency_ms'),
                step_count=len(steps)
            )
            latency_stats.append(stat)
        
        # Sort latency stats by turn_id (default sort order)
        latency_stats.sort(key=lambda x: x.turn_id)
        
        # Extract ToolActivity list from normalized_run.turns
        tool_activity = []
        
        for turn in turns:
            turn_id = turn.get('turn_id', 'unknown')
            steps = turn.get('steps', [])
            
            # Filter tool calls from steps
            tool_calls = []
            successful_count = 0
            failed_count = 0
            
            for step in steps:
                step_type = step.get('type', '')
                if step_type == 'tool_call':
                    tool_call_info = {
                        'name': step.get('name', 'unknown'),
                        'status': step.get('status', 'unknown'),
                        'latency_ms': step.get('latency_ms')
                    }
                    tool_calls.append(tool_call_info)
                    
                    # Count success/failure
                    status = step.get('status', '')
                    if status == 'success':
                        successful_count += 1
                    elif status in ['error', 'failed']:
                        failed_count += 1
            
            activity = ToolActivity(
                turn_id=turn_id,
                tool_calls=tool_calls,
                tool_call_count=len(tool_calls),
                successful_tools=successful_count,
                failed_tools=failed_count
            )
            tool_activity.append(activity)
        
        # Sort tool activity by turn_id (default sort order)
        tool_activity.sort(key=lambda x: x.turn_id)
        
        # Extract AdapterDiagnostics from normalized_run.adapter_stats
        adapter_stats = normalized_run.get('adapter_stats')
        
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
        
        # Extract and resolve evidence blocks
        evidence_details = []
        judge_reasoning = {}
        
        for rubric_result in rubric_results:
            rubric_id = rubric_result.get('rubric_id', 'unknown')
            scope = rubric_result.get('scope', 'run')
            turn_id = rubric_result.get('turn_id')
            
            # Extract evidence spans (if selectors present)
            evidence_spans = []
            evidence_fields_used = []
            
            # Check if rubric has selectors/evidence fields
            # Note: This is a simplified implementation - full selector resolution
            # would require parsing the rubric definition and resolving selectors
            # against the normalized_run context
            selectors = rubric_result.get('selectors', [])
            if not selectors:
                # No selectors present, emit empty evidence_spans
                self.logger(f"⚠ Warning: No selectors for rubric {rubric_id}, evidence will be empty")
            else:
                # For each selector, attempt to resolve content
                for selector in selectors:
                    # Simplified resolution - in a full implementation, this would
                    # use a proper selector engine to extract content from normalized_run
                    evidence_span = EvidenceSpan(
                        selector=str(selector),
                        resolved_content="[Evidence resolution not yet implemented]",
                        context_type=scope,
                        turn_id=turn_id if scope == "turn" else None,
                        source_location=None,  # Would be populated by full resolution
                        field_name=None  # Would be extracted from selector
                    )
                    evidence_spans.append(evidence_span)
                    evidence_fields_used.append(str(selector))
            
            # Determine resolution status
            if not selectors:
                resolution_status = "selectors_missing"
            elif not evidence_spans:
                resolution_status = "resolution_failed"
            elif len(evidence_spans) < len(selectors):
                resolution_status = "partial"
            else:
                resolution_status = "success"
            
            # Create evidence detail
            evidence_detail = RubricEvidenceDetail(
                rubric_id=rubric_id,
                scope=scope,
                turn_id=turn_id,
                evidence_spans=evidence_spans,
                evidence_fields_used=evidence_fields_used,
                resolution_status=resolution_status
            )
            evidence_details.append(evidence_detail)
            
            # Extract judge reasoning snippets
            within_judge_results = rubric_result.get('within_judge_results', [])
            reasoning_snippets = []
            
            # Determine if this rubric is categorical
            cross_judge = rubric_result.get('cross_judge_result', {})
            scoring_type = cross_judge.get('scoring_type', 'numeric')
            is_categorical = (scoring_type == 'categorical')
            
            for judge_result in within_judge_results:
                judge_id = judge_result.get('judge_id', 'unknown')
                score = judge_result.get('score')
                reasoning = judge_result.get('reasoning', '')
                
                # Create reasoning preview (max 200 chars)
                reasoning_preview = reasoning[:200]
                if len(reasoning) > 200:
                    reasoning_preview += '...'
                
                # Determine if score is numeric or categorical based on rubric scoring_type
                if is_categorical:
                    snippet = JudgeReasoningSnippet(
                        judge_id=judge_id,
                        score_numeric=None,
                        score_label=str(score) if score is not None else None,
                        reasoning=reasoning,
                        reasoning_preview=reasoning_preview
                    )
                else:
                    # Try to convert score to float, handle conversion errors gracefully
                    score_numeric = None
                    if score is not None:
                        try:
                            score_numeric = float(score)
                        except (ValueError, TypeError):
                            self.logger(f"⚠ Warning: Failed to convert score to float for judge {judge_id}: {score}")
                    
                    snippet = JudgeReasoningSnippet(
                        judge_id=judge_id,
                        score_numeric=score_numeric,
                        score_label=None,
                        reasoning=reasoning,
                        reasoning_preview=reasoning_preview
                    )
                reasoning_snippets.append(snippet)
            
            # Group reasoning snippets by rubric_id (and turn_id if turn-scoped)
            key = f"{rubric_id}:{turn_id}" if turn_id else rubric_id
            judge_reasoning[key] = reasoning_snippets
        
        # Build ArtifactPaths with file paths and checksums
        checksums = self.extract_checksums(artifacts)
        
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
        
        # Build ReportMetadata
        # Extract source artifact versions with explicit "unknown" fallback
        source_versions = {
            'adapter_version': 'unknown',
            'trace_eval_version': 'unknown'
        }
        
        if metadata:
            source_versions['adapter_version'] = metadata.get('adapter_version', 'unknown')
        
        if 'version' in trace_eval:
            source_versions['trace_eval_version'] = trace_eval.get('version', 'unknown')
        
        # Get generator version (could be from package version or hardcoded)
        generator_version = "1.0.0"  # TODO: Extract from package metadata
        
        report_metadata = ReportMetadata(
            generator_version=generator_version,
            generation_timestamp=datetime.now(),
            source_artifact_versions=source_versions,
            charts_enabled=True,  # Will be set by caller based on actual chart generation
            template_version="1.0.0"
        )
        
        # Build complete ReportViewModel
        view_model = ReportViewModel(
            run_summary=run_summary,
            trace_summary=trace_summary,
            rubric_scores=rubric_scores,
            judge_details=judge_details,
            latency_stats=latency_stats,
            tool_activity=tool_activity,
            adapter_diagnostics=adapter_diagnostics,
            artifact_paths=artifact_paths,
            report_metadata=report_metadata,
            evidence_details=evidence_details,
            judge_reasoning=judge_reasoning,
            diagnostic_warnings=[]  # Could be populated with warnings during processing
        )
        
        return view_model
    
    def render_template(
        self,
        view_model: 'ReportViewModel',
        charts: List[str]
    ) -> str:
        """
        Render Jinja2 template with view model and charts.

        This method creates a Jinja2 environment configured for secure HTML
        rendering with auto-escaping enabled to prevent XSS vulnerabilities.
        It loads the report.html.j2 template and renders it with the complete
        view model and chart HTML strings.

        Args:
            view_model: Complete ReportViewModel instance with all report data
            charts: List of chart HTML strings from Plotly (may be empty)

        Returns:
            Rendered HTML string ready for writing to file

        Raises:
            ReportGenerationError: If template loading or rendering fails

        Notes:
            - Auto-escaping is enabled for XSS prevention (Requirement 19.2, 20.2)
            - Template cache size is set to 10 for performance (Requirement 19.2)
            - Template is loaded from templates/report.html.j2 (Requirement 19.3)
            - All jinja2.TemplateError exceptions are caught and wrapped (Requirement 19.5)
        """
        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape
            import jinja2
        except ImportError as e:
            raise ReportGenerationError(
                f"Failed to import Jinja2: {e}\n"
                "Please install jinja2: pip install jinja2>=3.1.0"
            )

        try:
            # Get templates directory path (relative to this file)
            templates_dir = Path(__file__).parent / "templates"

            if not templates_dir.exists():
                raise ReportGenerationError(
                    f"Templates directory not found: {templates_dir}\n"
                    "Expected directory: agent_eval/evaluators/trace_eval/reporting/templates/"
                )

            # Create Jinja2 Environment with FileSystemLoader
            # - autoescape=True for XSS prevention (Requirement 19.2, 20.2)
            # - cache_size=10 for template caching (Requirement 19.2)
            env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                autoescape=select_autoescape(['html', 'xml', 'j2']),
                cache_size=10
            )

            # Load report.html.j2 template (Requirement 19.3)
            template_name = "report.html.j2"
            template = env.get_template(template_name)

            # Pass view_model and charts list to template.render() (Requirement 19.4)
            html_content = template.render(
                view_model=view_model,
                charts=charts
            )

            return html_content

        except jinja2.TemplateNotFound as e:
            raise ReportGenerationError(
                f"Template file not found: {e}\n"
                f"Expected file: {templates_dir / 'report.html.j2'}\n"
                "Please ensure report.html.j2 exists in the templates directory."
            )
        except jinja2.TemplateSyntaxError as e:
            raise ReportGenerationError(
                f"Template syntax error in {e.name} at line {e.lineno}: {e.message}\n"
                "Please check the template file for syntax errors."
            )
        except jinja2.TemplateError as e:
            # Catch all other Jinja2 template errors (Requirement 19.5)
            raise ReportGenerationError(
                f"Template rendering failed: {e}\n"
                "Please check the template file and view model data for issues."
            )
        except Exception as e:
            # Catch any other unexpected errors
            raise ReportGenerationError(
                f"Unexpected error during template rendering: {e}\n"
                f"Error type: {type(e).__name__}"
            )

    def create_latency_by_turn_chart(self, view_model: 'ReportViewModel') -> Optional[str]:
        """
        Create Plotly line chart showing latency by turn.

        This method generates an interactive line chart displaying total latency
        for each turn in the evaluation run. The chart helps identify performance
        bottlenecks and latency patterns across turns.

        Args:
            view_model: Complete ReportViewModel with latency_stats populated

        Returns:
            HTML string containing the Plotly chart with CDN-hosted Plotly library,
            or None if latency_stats is empty or all latencies are None

        Notes:
            - Uses total_latency_ms from latency_stats (Requirement 9.4)
            - Uses 0 if total_latency_ms is None (graceful handling)
            - Returns None for empty data (Requirement 9.7, 15.2)
            - Chart uses CDN-hosted Plotly (Requirement 10.4, 17.5)
            - Never raises exceptions (graceful degradation)
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            self.logger("⚠ Warning: Plotly not installed, skipping latency chart")
            return None

        # Handle empty latency_stats gracefully
        if not view_model.latency_stats:
            self.logger("⚠ Warning: No latency stats available, skipping latency chart")
            return None

        # Extract turn_ids and total_latency_ms (use 0 if None)
        turn_ids = []
        latencies = []

        for stat in view_model.latency_stats:
            turn_ids.append(stat.turn_id)
            # Use 0 if total_latency_ms is None
            latency_value = stat.total_latency_ms if stat.total_latency_ms is not None else 0
            latencies.append(latency_value)

        # If all latencies are 0 or None, skip chart
        if all(lat == 0 for lat in latencies):
            self.logger("⚠ Warning: All latencies are 0 or None, skipping latency chart")
            return None

        # Create Plotly line chart with go.Scatter
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=turn_ids,
            y=latencies,
            mode='lines+markers',
            name='Total Latency',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8, color='#1f77b4')
        ))

        # Set layout
        fig.update_layout(
            title="Latency by Turn",
            xaxis_title="Turn ID",
            yaxis_title="Latency (ms)",
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )

        # Return fig.to_html with CDN-hosted Plotly
        chart_html = fig.to_html(
            include_plotlyjs='cdn',
            div_id='latency_by_turn'
        )

        return chart_html

    def create_rubric_score_distribution_chart(self, rubric_scores: List['RubricScore']) -> Optional[str]:
        """
        Create bar chart showing rubric score distribution (numeric rubrics only).

        This method generates a Plotly bar chart displaying cross-judge scores
        for each numeric rubric. Categorical rubrics (is_categorical=True) are
        filtered out before charting (Gap #6).

        The chart uses color coding based on score thresholds:
        - Green: score >= 0.7 (high confidence)
        - Orange: 0.4 <= score < 0.7 (medium confidence)
        - Red: score < 0.4 (low confidence)

        Args:
            rubric_scores: List of RubricScore objects from view model

        Returns:
            HTML string containing embedded Plotly chart, or None if no numeric rubrics

        Notes:
            - Filters out categorical rubrics (is_categorical=True) before charting (Gap #6)
            - Logs info message if categorical rubrics excluded (Gap #13)
            - Returns None gracefully if no numeric rubrics available
            - Chart uses CDN-hosted Plotly library

        Validates: Requirements 9.1, 9.2, 9.7, 9.8, 10.4, 15.2, 17.4, 17.5
        """
        try:
            import plotly.graph_objects as go
        except ImportError as e:
            self.logger(f"⚠ Warning: Failed to import plotly: {e}")
            return None

        # Filter out categorical rubrics (Gap #6)
        numeric_rubrics = [rs for rs in rubric_scores if not rs.is_categorical]

        # Log info message if categorical rubrics were excluded (Gap #13)
        categorical_count = len(rubric_scores) - len(numeric_rubrics)
        if categorical_count > 0:
            self.logger(
                f"ℹ Info: Excluded {categorical_count} categorical rubric(s) from "
                f"Rubric Score Distribution chart (numeric rubrics only)"
            )

        # Handle empty rubric_scores gracefully (return None)
        if not numeric_rubrics:
            self.logger("⚠ Warning: No numeric rubrics available for score distribution chart")
            return None

        # Extract rubric_ids and cross_judge_scores from numeric rubrics only
        rubric_ids = [rs.rubric_id for rs in numeric_rubrics]
        scores = [rs.cross_judge_score for rs in numeric_rubrics]

        # Compute colors based on score thresholds
        # Green >= 0.7, Orange >= 0.4, Red < 0.4
        # Handle None scores (shouldn't happen for numeric rubrics, but be defensive)
        colors = []
        for score in scores:
            if score is None:
                colors.append('gray')  # Defensive: shouldn't happen for numeric rubrics
            elif score >= 0.7:
                colors.append('green')
            elif score >= 0.4:
                colors.append('orange')
            else:
                colors.append('red')

        # Create Plotly bar chart with go.Bar
        fig = go.Figure(data=[
            go.Bar(
                x=rubric_ids,
                y=scores,
                marker_color=colors
            )
        ])

        # Set layout: title, xaxis_title, yaxis_title, height=400
        fig.update_layout(
            title="Rubric Score Distribution (Numeric Only)",
            xaxis_title="Rubric ID",
            yaxis_title="Cross-Judge Score",
            height=400
        )

        # Return fig.to_html with CDN-hosted Plotly and specific div_id
        chart_html = fig.to_html(
            include_plotlyjs='cdn',
            div_id='rubric_score_dist'
        )

        return chart_html

    def create_judge_disagreement_chart(self, rubric_scores: List['RubricScore']) -> Optional[str]:
        """
        Create Plotly scatter plot showing judge disagreement signals for numeric rubrics.

        This chart visualizes disagreement between judges for each rubric, highlighting
        high-risk rubrics where disagreement exceeds the threshold (0.3). Categorical
        rubrics are excluded as their disagreement is not numeric.

        Args:
            rubric_scores: List of RubricScore objects from view model

        Returns:
            HTML string containing Plotly chart, or None if no numeric rubrics available

        Notes:
            - Filters out categorical rubrics (is_categorical=True) before charting (Gap #6)
            - Colors: red for high_risk_flag=True, blue otherwise
            - Adds horizontal line at y=0.3 to show high risk threshold
            - Returns None gracefully if no numeric rubrics (Requirement 15.2)
            - Chart title indicates "Numeric Only" to clarify exclusion (Gap #6)
        """
        try:
            import plotly.graph_objects as go
        except ImportError as e:
            self.logger(f"⚠ Warning: Failed to import plotly for chart generation: {e}")
            return None

        # Filter out categorical rubrics before charting (Gap #6)
        numeric_rubrics = [r for r in rubric_scores if not r.is_categorical]

        # Handle empty rubric_scores gracefully (return None)
        if not numeric_rubrics:
            self.logger("⚠ Warning: No numeric rubrics available for judge disagreement chart")
            return None

        # Log info message if categorical rubrics excluded from chart (Gap #13)
        categorical_count = len(rubric_scores) - len(numeric_rubrics)
        if categorical_count > 0:
            self.logger(f"ℹ Info: Excluded {categorical_count} categorical rubric(s) from judge disagreement chart")

        # Extract rubric_ids, disagreement_signals, and high_risk_flags from numeric rubrics only
        rubric_ids = []
        disagreements = []
        colors = []

        for rubric in numeric_rubrics:
            rubric_ids.append(rubric.rubric_id)
            disagreements.append(rubric.disagreement_signal)
            # Compute colors (red if high_risk_flag else blue)
            colors.append('red' if rubric.high_risk_flag else 'blue')

        # Create Plotly scatter plot
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=rubric_ids,
            y=disagreements,
            mode='markers',
            marker=dict(
                size=10,
                color=colors
            ),
            name='Disagreement Signal',
            hovertemplate='<b>%{x}</b><br>Disagreement: %{y:.3f}<extra></extra>'
        ))

        # Add horizontal line at y=0.3 with annotation
        fig.add_hline(
            y=0.3,
            line_dash="dash",
            line_color="red",
            annotation_text="High Risk Threshold"
        )

        # Set layout
        fig.update_layout(
            title="Judge Disagreement Analysis (Numeric Only)",
            xaxis_title="Rubric ID",
            yaxis_title="Disagreement Signal",
            height=400,
            showlegend=False
        )

        # Return fig.to_html with CDN-hosted Plotly
        return fig.to_html(
            include_plotlyjs='cdn',
            div_id='judge_disagreement'
        )

    def create_tool_activity_chart(self, view_model: 'ReportViewModel') -> Optional[str]:
        """
        Create Plotly stacked bar chart showing tool activity by turn.

        This method generates a stacked bar chart displaying successful and failed
        tool calls for each turn. The chart helps identify patterns in tool usage
        and failure rates across the evaluation run.

        Args:
            view_model: Complete ReportViewModel with tool_activity populated

        Returns:
            HTML string containing the Plotly chart with CDN-hosted Plotly library,
            or None if tool_activity is empty

        Notes:
            - Creates stacked bar chart with two traces: Successful (green) and Failed (red)
            - Uses tool_activity from view_model (Requirement 9.5)
            - Returns None for empty data (Requirement 9.7, 15.2)
            - Chart uses CDN-hosted Plotly (Requirement 10.4, 17.5)
            - Never raises exceptions (graceful degradation)

        Validates: Requirements 9.1, 9.5, 9.7, 9.8, 10.4, 15.2, 17.4, 17.5
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            self.logger("⚠ Warning: Plotly not installed, skipping tool activity chart")
            return None

        # Handle empty tool_activity gracefully
        if not view_model.tool_activity:
            self.logger("⚠ Warning: No tool activity data available, skipping tool activity chart")
            return None

        # Extract turn_ids, successful_tools, and failed_tools
        turn_ids = []
        successful = []
        failed = []

        for activity in view_model.tool_activity:
            turn_ids.append(activity.turn_id)
            successful.append(activity.successful_tools)
            failed.append(activity.failed_tools)

        # If all tool counts are 0, skip chart
        if all(s == 0 and f == 0 for s, f in zip(successful, failed)):
            self.logger("⚠ Warning: All tool counts are 0, skipping tool activity chart")
            return None

        # Create Plotly stacked bar chart with two traces
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Successful',
            x=turn_ids,
            y=successful,
            marker_color='green'
        ))

        fig.add_trace(go.Bar(
            name='Failed',
            x=turn_ids,
            y=failed,
            marker_color='red'
        ))

        # Set layout with stacked barmode
        fig.update_layout(
            title="Tool Activity by Turn",
            xaxis_title="Turn ID",
            yaxis_title="Tool Call Count",
            barmode='stack',
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )

        # Return fig.to_html with CDN-hosted Plotly
        chart_html = fig.to_html(
            include_plotlyjs='cdn',
            div_id='tool_activity'
        )

        return chart_html

    def create_confidence_penalty_chart(self, view_model: 'ReportViewModel') -> Optional[str]:
        """
        Create Plotly horizontal bar chart showing confidence penalty summary.

        This method generates a horizontal bar chart displaying aggregated confidence
        penalties by reason. The chart helps identify the most common sources of
        confidence degradation in the adapter processing.

        Args:
            view_model: Complete ReportViewModel with adapter_diagnostics populated

        Returns:
            HTML string containing the Plotly chart with CDN-hosted Plotly library,
            or None if confidence_penalties is empty

        Notes:
            - Aggregates penalties by reason (sum penalty values for each unique reason)
            - Creates horizontal bar chart (orientation='h') with orange bars
            - Dynamic height based on number of reasons: max(300, len(reasons) * 40)
            - Returns None for empty data (Requirement 9.7, 15.2)
            - Chart uses CDN-hosted Plotly (Requirement 10.4, 17.5)
            - Never raises exceptions (graceful degradation)

        Validates: Requirements 9.1, 9.6, 9.7, 9.8, 10.4, 15.2, 17.4, 17.5
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            self.logger("⚠ Warning: Plotly not installed, skipping confidence penalty chart")
            return None

        # Extract confidence_penalties from adapter_diagnostics
        confidence_penalties = view_model.adapter_diagnostics.confidence_penalties

        # Handle empty confidence_penalties gracefully
        if not confidence_penalties:
            self.logger("⚠ Warning: No confidence penalties available, skipping confidence penalty chart")
            return None

        # Aggregate penalties by reason (sum penalty values for each unique reason)
        penalty_by_reason = {}
        for penalty_entry in confidence_penalties:
            reason = penalty_entry.get('reason', 'unknown')
            penalty_val = penalty_entry.get('penalty', 0.0)
            penalty_by_reason[reason] = penalty_by_reason.get(reason, 0.0) + penalty_val

        # If no penalties after aggregation, skip chart
        if not penalty_by_reason:
            self.logger("⚠ Warning: No valid penalty data after aggregation, skipping confidence penalty chart")
            return None

        # Extract reasons and values for chart
        reasons = list(penalty_by_reason.keys())
        values = list(penalty_by_reason.values())

        # Create Plotly horizontal bar chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=values,
            y=reasons,
            orientation='h',
            marker_color='orange'
        ))

        # Set layout with dynamic height
        chart_height = max(300, len(reasons) * 40)

        fig.update_layout(
            title="Confidence Penalty Summary",
            xaxis_title="Total Penalty",
            yaxis_title="Reason",
            height=chart_height,
            template='plotly_white'
        )

        # Return fig.to_html with CDN-hosted Plotly
        chart_html = fig.to_html(
            include_plotlyjs='cdn',
            div_id='confidence_penalties'
        )

        return chart_html

    def generate_charts(self, view_model: 'ReportViewModel') -> List[str]:
        """
        Generate all Plotly charts as HTML strings.

        This method orchestrates the generation of all 5 chart types in a deterministic
        order for regression stability. Each chart generation is wrapped in try-except
        to handle individual chart failures gracefully without failing the entire report.

        The method calls chart creation methods in this specific order (Gap #8):
        1. rubric_score_distribution (numeric rubrics only)
        2. judge_disagreement (numeric rubrics only)
        3. latency_by_turn
        4. tool_activity
        5. confidence_penalty

        Args:
            view_model: Complete ReportViewModel with all data populated

        Returns:
            List of chart HTML strings (0-5 charts) in stable order.
            Each chart is an HTML string with CDN-hosted Plotly library.
            Returns empty list if no charts can be generated.

        Notes:
            - Calls all 5 chart creation methods in deterministic order (Gap #8)
            - Collects non-None chart HTML strings into list, preserving order
            - Wraps each chart call in try-except for graceful degradation (Gap #13)
            - Uses configured logger for all chart generation warnings (Gap #13)
            - Never raises exceptions (graceful degradation)
            - Returns list of 0-5 charts depending on data availability

        Validates: Requirements 9.1, 9.7, 9.8, 15.2, 17.4
        """
        charts = []

        # Chart 1: Rubric Score Distribution (numeric rubrics only)
        try:
            chart_html = self.create_rubric_score_distribution_chart(view_model.rubric_scores)
            if chart_html is not None:
                charts.append(chart_html)
        except Exception as e:
            self.logger(f"⚠ Warning: Failed to generate rubric_score_distribution chart: {e}")

        # Chart 2: Judge Disagreement (numeric rubrics only)
        try:
            chart_html = self.create_judge_disagreement_chart(view_model.rubric_scores)
            if chart_html is not None:
                charts.append(chart_html)
        except Exception as e:
            self.logger(f"⚠ Warning: Failed to generate judge_disagreement chart: {e}")

        # Chart 3: Latency by Turn
        try:
            chart_html = self.create_latency_by_turn_chart(view_model)
            if chart_html is not None:
                charts.append(chart_html)
        except Exception as e:
            self.logger(f"⚠ Warning: Failed to generate latency_by_turn chart: {e}")

        # Chart 4: Tool Activity by Turn
        try:
            chart_html = self.create_tool_activity_chart(view_model)
            if chart_html is not None:
                charts.append(chart_html)
        except Exception as e:
            self.logger(f"⚠ Warning: Failed to generate tool_activity chart: {e}")

        # Chart 5: Confidence Penalty Summary
        try:
            chart_html = self.create_confidence_penalty_chart(view_model)
            if chart_html is not None:
                charts.append(chart_html)
        except Exception as e:
            self.logger(f"⚠ Warning: Failed to generate confidence_penalty chart: {e}")

        return charts

    def write_report_atomic(self, html_content: str) -> str:
        """
        Write HTML report to file using atomic write operation.

        This method implements atomic file writing to ensure data integrity:
        1. Sanitizes run_id for safe filename generation
        2. Writes content to a temporary file
        3. Calls os.fsync() to ensure data is written to disk
        4. Atomically renames temp file to final path using os.replace()

        The atomic rename operation (os.replace) is atomic on both POSIX and
        Windows systems, ensuring that the report file is never left in a
        partially written state.

        Args:
            html_content: Complete HTML string to write to file

        Returns:
            Path to the generated report file as string

        Raises:
            IOError: If file write or rename operation fails

        Notes:
            - Uses sanitize_filename() to ensure safe filename (Requirement 16.1-16.5)
            - Writes to temp file first (.report_<run_id>.html.tmp) (Requirement 18.5)
            - Calls os.fsync() to ensure data written to disk (Requirement 18.4)
            - Uses os.replace() for atomic rename (POSIX and Windows) (Requirement 18.4)
            - Cleans up temp file if any step fails (Requirement 18.5)
            - Returns report_path as string (Requirement 1.5)

        Validates: Requirements 1.5, 15.4, 18.4, 18.5
        """
        import os

        # Sanitize run_id using sanitize_filename()
        safe_run_id = sanitize_filename(self.run_id)

        # Construct final report path: output_dir / f"report_{safe_run_id}.html"
        report_path = self.output_dir / f"report_{safe_run_id}.html"

        # Construct temp file path: output_dir / f".report_{safe_run_id}.html.tmp"
        temp_path = self.output_dir / f".report_{safe_run_id}.html.tmp"

        try:
            # Write html_content to temp file with UTF-8 encoding
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                # Flush Python buffers to OS
                f.flush()
                # Call os.fsync() on file descriptor to ensure data written to disk
                os.fsync(f.fileno())

            # Atomically rename temp file to final path using os.replace()
            # os.replace() is atomic on both POSIX and Windows
            os.replace(temp_path, report_path)

            return str(report_path)

        except IOError as e:
            # Handle IOError with descriptive error message
            # Clean up temp file if it exists
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception as cleanup_error:
                    self.logger(f"⚠ Warning: Failed to clean up temp file {temp_path}: {cleanup_error}")

            raise IOError(
                f"Failed to write report file: {e}\n"
                f"Attempted to write to: {report_path}\n"
                f"Temp file: {temp_path}"
            )
        except Exception as e:
            # Clean up temp file if any step fails
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception as cleanup_error:
                    self.logger(f"⚠ Warning: Failed to clean up temp file {temp_path}: {cleanup_error}")

            raise IOError(
                f"Unexpected error during report write: {e}\n"
                f"Error type: {type(e).__name__}\n"
                f"Attempted to write to: {report_path}"
            )






