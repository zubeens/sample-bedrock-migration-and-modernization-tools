"""
Trace Evaluator Runner - Main orchestration for trace evaluation.

This module orchestrates the complete evaluation flow:
1. Load input (NormalizedRun JSON)
2. Validate input against schema
3. Compute deterministic metrics
4. Load and merge rubrics
5. Load judge configuration
6. Build judge clients
7. Build JudgeJob queue
8. Execute jobs via worker pool
9. Aggregate results (within-judge and cross-judge)
10. Write output files (trace_eval.json, results.json)
11. Generate HTML report (reads trace_eval.json and results.json from step 10)

NOTE: This runner only accepts pre-normalized input (NormalizedRun JSON).
Adapter integration must be handled in CLI/pipeline layer before invoking this runner.
"""

import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING

from agent_eval.evaluators.trace_eval.json_utils import SafeJSONEncoder

if TYPE_CHECKING:
    from agent_eval.judges.judge_config_schema import JudgeConfig
    from agent_eval.evaluators.trace_eval.input_validator import InputValidator
    from agent_eval.evaluators.trace_eval.rubric_loader import RubricLoader
    from agent_eval.judges.judge_config_schema import JudgeConfigLoader
    from agent_eval.evaluators.trace_eval.deterministic_metrics import DeterministicMetrics
    from agent_eval.evaluators.trace_eval.judging.job_builder import JobBuilder
    from agent_eval.evaluators.trace_eval.judging.queue_runner import WorkerPool
    from agent_eval.evaluators.trace_eval.judging.aggregator import Aggregator
    from agent_eval.evaluators.trace_eval.output_writer import OutputWriter


# Canonical status definitions - used consistently across WorkerPool, Aggregator, and Runner
CANONICAL_SUCCESS_STATUSES = {"success"}
CANONICAL_FAILURE_STATUSES = {"failure", "timeout", "invalid_response", "cancelled", "error", "failed"}


def _rubric_id(r) -> Optional[str]:
    """Extract rubric_id from rubric object or dict. Returns None if not found."""
    if hasattr(r, 'rubric_id'):
        return r.rubric_id
    if isinstance(r, dict):
        return r.get('rubric_id')
    return None


def _rubric_scale(r) -> Optional[Any]:
    """
    Extract scoring_scale from rubric object or dict.
    
    Returns None if not found. The returned value may be:
    - A dict with type/min/max/values keys
    - A ScoringScale dataclass
    - An arbitrary object with .type/.min/.max/.values attributes
    
    Callers must handle all three forms (see _aggregate_results for conversion).
    Return type is Optional[Any] because the rubric source is not constrained
    to a single schema — this is honest, not loose.
    """
    if hasattr(r, 'scoring_scale'):
        return r.scoring_scale
    if isinstance(r, dict):
        return r.get('scoring_scale')
    return None


class TraceEvaluatorError(Exception):
    """Base exception for trace evaluator errors."""
    EXIT_CODE = 1


class ConfigError(TraceEvaluatorError):
    """Configuration error (judge config, rubrics)."""
    EXIT_CODE = 2


class InputValidationError(TraceEvaluatorError):
    """Input validation error (schema, format)."""
    EXIT_CODE = 3


class AdapterError(TraceEvaluatorError):
    """
    Adapter execution error.
    
    NOTE: This runner does not perform adapter work (see module docstring).
    Retained for backward compatibility with CLI/pipeline error handling that
    may catch this type. Remove once all callers are confirmed migrated.
    """
    EXIT_CODE = 4


class AggregationError(TraceEvaluatorError):
    """Aggregation error."""
    EXIT_CODE = 5


class OutputWriteError(TraceEvaluatorError):
    """Output writing error."""
    EXIT_CODE = 6


class TraceEvaluator:
    """Main orchestrator for trace evaluation."""
    
    def __init__(
        self,
        input_path: str,
        judge_config_path: str,
        output_dir: str,
        rubrics_path: Optional[str] = None,
        verbose: bool = False,
        debug: bool = False,
        skip_report: bool = False,
        enable_charts: bool = True
    ):
        """
        Initialize trace evaluator.
        
        ARCHITECTURE: TraceEvaluator only accepts normalized input.
        Adapter logic must be handled in CLI/pipeline layer.
        
        Args:
            input_path: Path to NormalizedRun JSON file (must be pre-normalized)
            judge_config_path: Path to judges.yaml configuration
            output_dir: Directory for output files
            rubrics_path: Optional path to user rubrics.yaml
            verbose: Enable verbose output
            debug: Enable debug mode with detailed error traces
            skip_report: Skip HTML report generation (Step 11)
            enable_charts: Enable chart generation in HTML reports (default: True)
        """
        self.input_path = Path(input_path)
        self.judge_config_path = Path(judge_config_path)
        self.output_dir = Path(output_dir)
        self.rubrics_path = Path(rubrics_path) if rubrics_path else None
        self.verbose = verbose
        self.debug = debug
        self.skip_report = skip_report
        self.enable_charts = enable_charts
        
        # Validate paths exist
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if not self.judge_config_path.exists():
            raise FileNotFoundError(f"Judge config file not found: {judge_config_path}")
        
        if self.rubrics_path and not self.rubrics_path.exists():
            raise FileNotFoundError(f"Rubrics file not found: {rubrics_path}")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components (lazy loaded)
        self._validator = None
        self._rubric_loader = None
        self._judge_config_loader = None
        self._deterministic_metrics = None
        self._job_builder = None
        self._aggregator = None
        self._output_writer = None
        
        # Feature detection flags for Aggregator scoring_scale support
        self._agg_supports_scoring_scale_within = False
        self._agg_supports_scoring_scale_cross = False
    
    def _log(self, message: str, force: bool = False) -> None:
        """
        Log message if verbose mode is enabled.
        
        Args:
            message: Message to log
            force: Always print regardless of verbose setting
        """
        if self.verbose or force:
            print(message)
    
    def _get_validator(self) -> "InputValidator":
        """Lazy load input validator."""
        if self._validator is None:
            from agent_eval.evaluators.trace_eval.input_validator import InputValidator
            self._validator = InputValidator()
        return self._validator
    
    def _get_rubric_loader(self) -> "RubricLoader":
        """Lazy load rubric loader."""
        if self._rubric_loader is None:
            from agent_eval.evaluators.trace_eval.rubric_loader import RubricLoader
            self._rubric_loader = RubricLoader()
        return self._rubric_loader
    
    def _get_judge_config_loader(self) -> "JudgeConfigLoader":
        """Lazy load judge config loader."""
        if self._judge_config_loader is None:
            from agent_eval.judges.judge_config_schema import JudgeConfigLoader
            self._judge_config_loader = JudgeConfigLoader()
        return self._judge_config_loader
    
    def _get_deterministic_metrics(self) -> "DeterministicMetrics":
        """Lazy load deterministic metrics computer."""
        if self._deterministic_metrics is None:
            from agent_eval.evaluators.trace_eval.deterministic_metrics import DeterministicMetrics
            self._deterministic_metrics = DeterministicMetrics()
        return self._deterministic_metrics
    
    def _get_job_builder(self) -> "JobBuilder":
        """Lazy load job builder."""
        if self._job_builder is None:
            from agent_eval.evaluators.trace_eval.judging.job_builder import JobBuilder
            self._job_builder = JobBuilder()
        return self._job_builder
    
    def _get_worker_pool(self, judge_clients: Dict[str, Any], max_concurrency: int = 10) -> "WorkerPool":
        """
        Create worker pool with judge clients (no caching).
        
        Note: WorkerPool is not cached to avoid stale judge_clients if
        TraceEvaluator is reused with different configurations.
        
        Args:
            judge_clients: Dictionary mapping judge_id to JudgeClient instances
            max_concurrency: Maximum concurrent jobs
            
        Returns:
            WorkerPool instance
        """
        from agent_eval.evaluators.trace_eval.judging.queue_runner import WorkerPool
        return WorkerPool(
            judge_clients=judge_clients,
            max_concurrency=max_concurrency
        )
    
    def _build_judge_clients(self, judge_config: "JudgeConfig") -> Dict[str, Any]:
        """
        Build judge client instances from judge configuration.
        
        Delegates to client_factory module for provider selection and instantiation.
        
        Args:
            judge_config: JudgeConfig object with judges list
            
        Returns:
            Dictionary mapping judge_id to JudgeClient instance
            
        Raises:
            ConfigError: If judge client instantiation fails
        """
        from agent_eval.judges.client_factory import build_judge_clients, JudgeClientFactoryError
        
        try:
            judge_clients = build_judge_clients(judge_config)
            
            # Log built clients
            for judge in judge_config.judges:
                self._log(f"✓ Built {judge.provider} judge client: {judge.judge_id}")
            
            return judge_clients
        except JudgeClientFactoryError as e:
            raise ConfigError(str(e)) from e
    
    def _get_aggregator(self) -> "Aggregator":
        """Lazy load aggregator with feature detection."""
        if self._aggregator is None:
            from agent_eval.evaluators.trace_eval.judging.aggregator import Aggregator
            import inspect
            
            self._aggregator = Aggregator()
            
            # Feature detect scoring_scale parameter support
            within_sig = inspect.signature(self._aggregator.aggregate_within_judge)
            cross_sig = inspect.signature(self._aggregator.aggregate_cross_judge)
            
            self._agg_supports_scoring_scale_within = 'scoring_scale' in within_sig.parameters
            self._agg_supports_scoring_scale_cross = 'scoring_scale' in cross_sig.parameters
            
        return self._aggregator
    
    def _get_output_writer(self) -> "OutputWriter":
        """Lazy load output writer."""
        if self._output_writer is None:
            from agent_eval.evaluators.trace_eval.output_writer import OutputWriter
            self._output_writer = OutputWriter(output_dir=str(self.output_dir))
        return self._output_writer
    
    def _validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input against NormalizedRun schema.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            Validated NormalizedRun data
            
        Raises:
            InputValidationError: If validation fails
        """
        try:
            validator = self._get_validator()
            self._log("Validating input against NormalizedRun schema...")
            validated_data = validator.validate(input_data)
            self._log("✓ Input validation passed")
            return validated_data
            
        except Exception as e:
            raise InputValidationError(f"Input validation failed: {e}") from e
    
    def _load_rubrics(self) -> List:
        """
        Load and merge rubrics.
        
        Returns:
            List of merged rubrics
            
        Raises:
            ConfigError: If rubric loading fails
        """
        try:
            rubric_loader = self._get_rubric_loader()
            
            self._log("Loading default rubrics...")
            default_rubrics = rubric_loader.load_default_rubrics()
            self._log(f"✓ Loaded {len(default_rubrics)} default rubrics")
            
            if self.rubrics_path:
                self._log(f"Loading user rubrics from {self.rubrics_path}...")
                user_rubrics = rubric_loader.load_user_rubrics(str(self.rubrics_path))
                self._log(f"✓ Loaded {len(user_rubrics)} user rubrics")
                
                self._log("Merging rubrics...")
                merged_rubrics = rubric_loader.merge_rubrics(default_rubrics, user_rubrics)
                self._log(f"✓ Merged to {len(merged_rubrics)} enabled rubrics")
                return merged_rubrics
            else:
                return default_rubrics
                
        except Exception as e:
            raise ConfigError(f"Rubric loading failed: {e}") from e
    
    def _load_judge_config(self) -> "JudgeConfig":
        """
        Load and validate judge configuration.
        
        Returns:
            Judge configuration (JudgeConfig object)
            
        Raises:
            ConfigError: If judge config loading fails
        """
        try:
            judge_config_loader = self._get_judge_config_loader()
            
            self._log(f"Loading judge configuration from {self.judge_config_path}...")
            judge_config = judge_config_loader.load(str(self.judge_config_path))
            
            judge_count = len(judge_config.judges)
            
            # Enforce 1-5 judges requirement (already validated by JudgeConfig.__post_init__)
            if judge_count < 1:
                raise ConfigError("At least 1 judge required")
            if judge_count > 5:
                raise ConfigError("Maximum 5 judges allowed")
            
            self._log(f"✓ Loaded configuration for {judge_count} judge(s)")
            
            return judge_config
            
        except ConfigError:
            raise
        except Exception as e:
            raise ConfigError(f"Judge config loading failed: {e}") from e
    
    def _compute_deterministic_metrics(self, normalized_run: Dict[str, Any]):
        """
        Compute deterministic metrics from NormalizedRun.
        
        Args:
            normalized_run: Validated NormalizedRun data
            
        Returns:
            MetricsResult object (not dict)
            
        Raises:
            TraceEvaluatorError: If metrics computation fails
        """
        try:
            metrics_computer = self._get_deterministic_metrics()
            
            self._log("Computing deterministic metrics...")
            metrics = metrics_computer.compute(normalized_run)
            
            self._log(f"✓ Computed metrics: {metrics.turn_count} turns, {metrics.tool_call_count} tool calls")
            
            return metrics  # Return MetricsResult object, not dict
            
        except Exception as e:
            raise TraceEvaluatorError(f"Deterministic metrics computation failed: {e}") from e
    
    def _build_judge_jobs(
        self,
        normalized_run: Dict[str, Any],
        rubrics: List,
        judge_config: "JudgeConfig",
        deterministic_metrics
    ) -> List:
        """
        Build JudgeJob queue.
        
        Args:
            normalized_run: Validated NormalizedRun data
            rubrics: List of rubrics
            judge_config: Judge configuration (JudgeConfig object)
            deterministic_metrics: Computed deterministic metrics (MetricsResult object)
            
        Returns:
            List of JudgeJobs
            
        Raises:
            TraceEvaluatorError: If job building fails
        """
        try:
            job_builder = self._get_job_builder()
            
            self._log("Building JudgeJob queue...")
            jobs = job_builder.build_jobs(
                normalized_run=normalized_run,
                rubrics=rubrics,
                judges=judge_config.judges,
                deterministic_metrics=deterministic_metrics
            )
            
            self._log(f"✓ Built {len(jobs)} JudgeJobs")
            
            return jobs
            
        except Exception as e:
            raise TraceEvaluatorError(f"JudgeJob building failed: {e}") from e
    
    def _execute_jobs(self, jobs: List, judge_clients: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute JudgeJobs via Worker Pool.
        
        Args:
            jobs: List of JudgeJobs
            judge_clients: Dictionary mapping judge_id to JudgeClient instances
            
        Returns:
            Execution result with statistics (normalized for output schema)
            
        Raises:
            TraceEvaluatorError: If execution fails critically
        """
        try:
            worker_pool = self._get_worker_pool(judge_clients)
            
            # Output path for judge_runs.jsonl
            judge_runs_path = self.output_dir / "judge_runs.jsonl"
            
            self._log(f"Executing {len(jobs)} jobs with Worker Pool...")
            self._log(f"Results will be written to: {judge_runs_path}")
            
            execution_result = worker_pool.run(
                jobs=jobs,
                output_path=str(judge_runs_path)
            )
            
            self._log(f"✓ Execution complete: {execution_result.successful_job_count}/{execution_result.total_job_count} succeeded")
            
            if execution_result.failed_job_count > 0:
                self._log(f"⚠ {execution_result.failed_job_count} jobs failed")
            
            # Translate internal execution model to output schema format
            # This normalization happens at the boundary between execution and output layers
            return {
                "total_jobs": execution_result.total_job_count,
                "completed_jobs": execution_result.successful_job_count,
                "failed_jobs": execution_result.failed_job_count,
                "skipped_jobs": execution_result.skipped_job_count,
                "failure_ratio": execution_result.failure_ratio,
                "failed_job_ids": execution_result.failed_job_ids,
                "sum_job_latency_ms": execution_result.sum_job_latency_ms,
                "duration_seconds": execution_result.wall_time_seconds
            }
            
        except Exception as e:
            raise TraceEvaluatorError(f"Job execution failed: {e}") from e
    
    def _aggregate_results(
        self,
        judge_runs_path: Path,
        rubrics: List,
        run_id: str
    ) -> Dict[str, Any]:
        """
        Aggregate judge results (within-judge and cross-judge).
        
        Args:
            judge_runs_path: Path to judge_runs.jsonl
            rubrics: List of rubrics (Rubric objects or dicts)
            run_id: Current run ID to filter results (prevents cross-contamination)
            
        Returns:
            Aggregated results with rubric_results and judge_summary
            
        Raises:
            AggregationError: If aggregation fails
        """
        try:
            from .judging.models import JobResult
            from .judging.aggregator import ScoringScale
            
            aggregator = self._get_aggregator()
            
            self._log("Aggregating judge results...")
            
            # Load judge runs from JSONL with validation
            judge_runs = []
            line_num = 0
            
            # Track aggregation stats for debugging
            aggregation_stats = {
                "lines_total": 0,
                "lines_parsed": 0,
                "lines_skipped_bad_json": 0,
                "lines_skipped_missing_fields": 0,
                "lines_skipped_bad_jobresult": 0,
                "lines_skipped_runid_mismatch": 0
            }
            
            with open(judge_runs_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line_num += 1
                    aggregation_stats["lines_total"] += 1
                    
                    try:
                        job_result_dict = json.loads(line)
                        
                        # Validate required fields for aggregation (minimal set)
                        # Only require fields actually needed for grouping and aggregation
                        required_fields = ["job_id", "rubric_id", "judge_id", "status"]
                        missing_fields = [f for f in required_fields if f not in job_result_dict]
                        if missing_fields:
                            aggregation_stats["lines_skipped_missing_fields"] += 1
                            self._log(f"⚠ Warning: Skipping JSONL line {line_num} - missing fields: {missing_fields}")
                            continue
                        
                        # Use JobResult.from_dict for proper validation and construction
                        try:
                            job_result = JobResult.from_dict(job_result_dict)
                        except (AttributeError, ValueError, TypeError) as e:
                            aggregation_stats["lines_skipped_bad_jobresult"] += 1
                            self._log(f"⚠ Warning: Skipping JSONL line {line_num} - JobResult construction failed: {e}")
                            continue
                        
                        # Filter by run_id to prevent cross-contamination
                        # Treat missing/None/empty run_id as acceptable (legacy format)
                        if job_result.run_id and job_result.run_id != run_id:
                            aggregation_stats["lines_skipped_runid_mismatch"] += 1
                            self._log(f"⚠ Warning: Skipping JSONL line {line_num} - run_id mismatch (expected {run_id}, got {job_result.run_id})")
                            continue
                        
                        # Normalize turn_id: treat empty string as None for run-level rubrics
                        # Use dataclass replace to avoid frozen instance errors
                        if job_result.turn_id == "":
                            from dataclasses import replace
                            job_result = replace(job_result, turn_id=None)
                        
                        aggregation_stats["lines_parsed"] += 1
                        judge_runs.append(job_result)
                        
                    except json.JSONDecodeError as e:
                        aggregation_stats["lines_skipped_bad_json"] += 1
                        self._log(f"⚠ Warning: Skipping malformed JSONL line {line_num}: {e}")
                        continue
                    except (ValueError, KeyError, TypeError) as e:
                        aggregation_stats["lines_skipped_bad_jobresult"] += 1
                        self._log(f"⚠ Warning: Skipping invalid JSONL line {line_num}: {e}")
                        continue
            
            if not judge_runs:
                self._log("⚠ Warning: No valid judge runs found for aggregation")
                self._log(f"  Aggregation stats: {aggregation_stats}")
                return {
                    "rubric_results": [],
                    "judge_summary": {
                        "total_jobs": 0,
                        "successful_jobs": 0,
                        "failed_jobs": 0
                    },
                    "cross_judge_results": [],
                    "aggregation_stats": aggregation_stats
                }
            
            # Build rubric lookup
            rubric_lookup = {}
            for r in rubrics:
                rid = _rubric_id(r)
                if rid:
                    rubric_lookup[rid] = r
            
            # Group results by (rubric_id, turn_id) for aggregation
            from collections import defaultdict
            grouped_results = defaultdict(lambda: defaultdict(list))
            unknown_rubric_ids = set()  # Track rubric IDs not in current config
            
            for job_result in judge_runs:
                rubric_id = job_result.rubric_id
                turn_id = job_result.turn_id  # None for run-level
                judge_id = job_result.judge_id
                
                # Track unknown rubric IDs (config drift detection)
                if rubric_id not in rubric_lookup:
                    unknown_rubric_ids.add(rubric_id)
                
                # Group by (rubric_id, turn_id, judge_id) for within-judge aggregation
                grouped_results[(rubric_id, turn_id)][judge_id].append(job_result)
            
            # Warn about unknown rubric IDs (possible config drift)
            if unknown_rubric_ids:
                self._log(f"⚠ Warning: Found {len(unknown_rubric_ids)} rubric ID(s) in JSONL not present in current rubric config:")
                for rid in sorted(unknown_rubric_ids):
                    self._log(f"  - {rid}")
                self._log("  This may indicate config drift or stale JSONL data.")
            
            # Perform within-judge and cross-judge aggregation
            cross_judge_results = []
            
            for (rubric_id, turn_id), judge_results_dict in grouped_results.items():
                # Get rubric for scoring scale using helper function
                rubric = rubric_lookup.get(rubric_id)
                scoring_scale = None
                if rubric:
                    scale_data = _rubric_scale(rubric)
                    if scale_data:
                        try:
                            # Handle dict, ScoringScale object, or dataclass
                            if isinstance(scale_data, ScoringScale):
                                # Already a ScoringScale object
                                scoring_scale = scale_data
                            elif isinstance(scale_data, dict):
                                # Dict format
                                scoring_scale = ScoringScale(
                                    type=scale_data.get("type", "numeric"),
                                    min=scale_data.get("min"),
                                    max=scale_data.get("max"),
                                    values=scale_data.get("values")
                                )
                            elif hasattr(scale_data, 'type'):
                                # Dataclass or object with attributes
                                scoring_scale = ScoringScale(
                                    type=getattr(scale_data, 'type', 'numeric'),
                                    min=getattr(scale_data, 'min', None),
                                    max=getattr(scale_data, 'max', None),
                                    values=getattr(scale_data, 'values', None)
                                )
                        except (ValueError, KeyError, AttributeError) as e:
                            self._log(f"⚠ Warning: Invalid scoring scale for rubric {rubric_id}: {e}")
                
                # Within-judge aggregation for each judge
                within_judge_results = []
                for judge_id, results in judge_results_dict.items():
                    # Use feature detection flags instead of try/except
                    if self._agg_supports_scoring_scale_within:
                        within_result = aggregator.aggregate_within_judge(
                            results=results,
                            judge_id=judge_id,
                            rubric_id=rubric_id,
                            turn_id=turn_id,
                            scoring_scale=scoring_scale
                        )
                    else:
                        within_result = aggregator.aggregate_within_judge(
                            results=results,
                            judge_id=judge_id,
                            rubric_id=rubric_id,
                            turn_id=turn_id
                        )
                    within_judge_results.append(within_result)
                
                # Cross-judge aggregation
                if self._agg_supports_scoring_scale_cross:
                    cross_result = aggregator.aggregate_cross_judge(
                        within_judge_results=within_judge_results,
                        rubric_id=rubric_id,
                        turn_id=turn_id,
                        scoring_scale=scoring_scale
                    )
                else:
                    cross_result = aggregator.aggregate_cross_judge(
                        within_judge_results=within_judge_results,
                        rubric_id=rubric_id,
                        turn_id=turn_id
                    )
                cross_judge_results.append(cross_result)
            
            # Build judge summary - use canonical status definitions
            # Note: total_jobs reflects parsed JSONL job results
            # attempted_jobs_total (added later in run()) shows total jobs attempted
            judge_summary = {
                "total_jobs": len(judge_runs),  # Parsed job results count
                "successful_jobs": sum(1 for r in judge_runs if r.status in CANONICAL_SUCCESS_STATUSES),
                "failed_jobs": sum(1 for r in judge_runs if r.status in CANONICAL_FAILURE_STATUSES),
                "parsed_job_results": len(judge_runs)  # Explicit count of parsed results (same as total_jobs)
            }
            
            self._log(f"✓ Aggregation complete: {len(judge_runs)} judge runs processed")
            self._log(f"  - {len(cross_judge_results)} rubric evaluations aggregated")
            self._log(f"  - Aggregation stats: {aggregation_stats}")
            
            # Add unknown rubric IDs to aggregation stats for monitoring
            aggregation_stats["unknown_rubric_ids"] = sorted(list(unknown_rubric_ids))
            aggregation_stats["unknown_rubric_count"] = len(unknown_rubric_ids)
            
            return {
                "rubric_results": cross_judge_results,  # List of CrossJudgeResult objects
                "judge_summary": judge_summary,
                "cross_judge_results": cross_judge_results,  # Keep for compatibility
                "aggregation_stats": aggregation_stats  # For debugging and production monitoring
            }
            
        except AggregationError:
            raise
        except (OSError, json.JSONDecodeError, ValueError, KeyError) as e:
            # Operational failures during JSONL parsing or aggregation logic.
            raise AggregationError(f"Aggregation failed: {e}") from e
        except Exception as e:
            # Unexpected errors (likely programmer bugs).  Still wrapped as
            # AggregationError for runner UX, but the message flags it as
            # potentially a bug so it doesn't hide silently.
            raise AggregationError(
                f"Aggregation failed (unexpected — may be a bug): {e}"
            ) from e
    
    def _generate_html_report(self, run_id: str) -> str:
        """
        Generate HTML report from canonical artifacts.
        
        Pre-flight: verifies that trace_eval.json and results.json exist in
        output_dir before invoking generate_report(). This turns a confusing
        downstream error into a clear, early failure message.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Path to generated HTML report
            
        Raises:
            FileNotFoundError: If required input artifacts are missing
            Exception: If report generation fails (caller handles)
        """
        # Pre-flight: verify required artifacts exist before report generation
        trace_eval_path = self.output_dir / "trace_eval.json"
        results_path = self.output_dir / "results.json"
        missing = []
        if not trace_eval_path.exists():
            missing.append(str(trace_eval_path))
        if not results_path.exists():
            missing.append(str(results_path))
        if missing:
            raise FileNotFoundError(
                f"Report generation requires artifacts from Step 10 that are missing: {', '.join(missing)}"
            )
        
        from agent_eval.evaluators.trace_eval.reporting.html_report import generate_report
        
        report_path = generate_report(
            output_dir=str(self.output_dir),
            run_id=run_id,
            enable_charts=self.enable_charts,
            logger=self._log
        )
        
        return report_path
    
    def _update_results_with_report(self, report_path: Optional[str], report_status: str) -> bool:
        """
        Update results.json with report path and generation status.
        
        This method updates the existing results.json file after report generation
        using atomic write pattern (temp file + replace + fsync + dir fsync) for safety.
        
        Checksum handling:
        - Prefers artifact_checksums key (report_builder standard)
        - Falls back to artifact_hashes key (output_writer legacy)
        - Initializes artifact_checksums if neither key exists
        - Recomputes checksums for all artifacts listed in artifact_paths
        - Does NOT self-hash results.json (would be invalidated by the write itself)
        
        Failure mode:
        - Logs a warning AND returns False on operational failures (OSError,
          JSON decode/encode) so the caller can decide whether to treat it
          as degraded or fatal.
        - Does NOT catch broad Exception — programmer bugs (KeyError,
          TypeError, AttributeError) are allowed to propagate so they
          surface during development rather than hiding behind a warning.
        
        Args:
            report_path: Path to generated HTML report (None if failed/skipped)
            report_status: Status of report generation ("success", "failed", "skipped")
            
        Returns:
            True if update succeeded, False otherwise
        """
        import os
        
        try:
            results_path = self.output_dir / "results.json"
            
            if not results_path.exists():
                self._log(f"⚠ Warning: results.json not found, cannot update with report info")
                return False
            
            with open(results_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            if "artifact_paths" not in results:
                results["artifact_paths"] = {}
            results["artifact_paths"]["report"] = report_path
            
            if "execution_stats" not in results:
                results["execution_stats"] = {}
            results["execution_stats"]["report_generation_status"] = report_status
            
            # Resolve checksum key: prefer artifact_checksums (report_builder standard),
            # fall back to artifact_hashes (output_writer legacy),
            # initialize artifact_checksums if neither exists.
            if "artifact_checksums" in results:
                checksum_key = "artifact_checksums"
            elif "artifact_hashes" in results:
                checksum_key = "artifact_hashes"
            else:
                checksum_key = "artifact_checksums"
                results[checksum_key] = {}
            
            # Recompute checksums for all artifacts except results.json itself.
            # results.json cannot self-hash (the write would invalidate the hash).
            output_writer = self._get_output_writer()
            for artifact_name, artifact_path in results["artifact_paths"].items():
                if artifact_name == "results" or not artifact_path:
                    continue
                try:
                    results[checksum_key][artifact_name] = output_writer.compute_file_hash(artifact_path)
                except OSError:
                    results[checksum_key][artifact_name] = None
            
            temp_path = results_path.with_suffix('.json.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, cls=SafeJSONEncoder)
                f.flush()
                os.fsync(f.fileno())
            
            temp_path.replace(results_path)
            
            # Directory fsync: ensures the rename is durable on crash.
            # Without this, the directory entry update may be lost on power failure.
            dir_fd = os.open(str(self.output_dir), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
            
            self._log(f"✓ Updated results.json with report info (checksum key: {checksum_key})")
            return True
            
        except (OSError, json.JSONDecodeError, ValueError) as e:
            self._log(f"⚠ Warning: Failed to update results.json with report info: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return False
    
    def _write_outputs(
        self,
        run_id: str,
        deterministic_metrics,
        aggregated_results: Dict[str, Any],
        execution_stats: Dict[str, Any],
        rubrics: List,
        judge_config: "JudgeConfig",
        normalized_run: Dict[str, Any],
        report_path: Optional[str] = None,
        report_generation_status: str = "pending"
    ) -> None:
        """
        Write canonical output files.
        
        Args:
            run_id: Run ID
            deterministic_metrics: Computed deterministic metrics (MetricsResult object)
            aggregated_results: Aggregated judge results with cross_judge_results
            execution_stats: Execution statistics
            rubrics: List of rubrics for config hash
            judge_config: Judge configuration (JudgeConfig object) for config hash
            normalized_run: Original input for input hash
            report_path: Optional path to generated HTML report (None if not yet generated)
            report_generation_status: Status of report generation ("pending", "success", "failed", "skipped")
            
        Raises:
            OutputWriteError: If output writing fails
        """
        try:
            from dataclasses import asdict
            
            output_writer = self._get_output_writer()
            
            self._log("Writing output files...")
            
            # Extract cross_judge_results for building outputs
            cross_judge_results = aggregated_results.get("cross_judge_results", [])
            
            # Build rubric_results for trace_eval.json
            rubric_results_for_trace_eval = output_writer.build_rubric_results_for_trace_eval(
                cross_judge_results=cross_judge_results
            )
            
            # Write trace_eval.json
            trace_eval_path = output_writer.write_trace_eval(
                run_id=run_id,
                deterministic_metrics=deterministic_metrics,
                rubric_results=rubric_results_for_trace_eval,
                judge_summary=aggregated_results.get("judge_summary", {})
            )
            self._log(f"✓ Wrote {trace_eval_path}")
            
            # Build artifact_paths for results.json
            artifact_paths = {
                "judge_runs": str(self.output_dir / "judge_runs.jsonl"),
                "trace_eval": str(trace_eval_path),
                "report": report_path if report_path else None
            }
            
            # Build execution_stats copy to avoid mutating caller's dict
            execution_stats_for_output = dict(execution_stats)
            execution_stats_for_output["report_generation_status"] = report_generation_status
            
            # Extract judge_disagreements
            judge_disagreements = output_writer.extract_judge_disagreements(
                cross_judge_results=cross_judge_results
            )
            
            # Build rubric_results for results.json (per-rubric, per-turn structure)
            rubric_results_for_results_json = output_writer.build_rubric_results_for_results_json(
                cross_judge_results=cross_judge_results
            )
            
            # Build rubrics_config - handle both Rubric objects and dicts
            # Fail-fast if any rubric can't be serialized (affects fingerprint integrity)
            rubrics_list = []
            for r in rubrics:
                try:
                    if hasattr(r, 'to_dict'):
                        # Rubric object with to_dict method
                        rubrics_list.append(r.to_dict())
                    elif isinstance(r, dict):
                        # Already a dict
                        rubrics_list.append(r)
                    else:
                        # Fallback: try to convert to dict
                        rubrics_list.append(dict(r))
                except (TypeError, ValueError) as e:
                    # Fail-fast: rubric serialization failure affects fingerprint integrity
                    raise OutputWriteError(
                        f"Failed to serialize rubric for config hash: {r}. "
                        f"This would produce misleading fingerprints. Error: {e}"
                    ) from e
            
            # Convert JudgeConfig object to dict for hashing
            # Use dataclasses.asdict to recursively convert JudgeConfig and Judge objects
            judge_config_dict = asdict(judge_config)
            
            # Write results.json with correct signature
            results_path = output_writer.write_results_json(
                run_id=run_id,
                rubrics_config={"rubrics": rubrics_list},
                judge_config=judge_config_dict,
                input_data=normalized_run,
                deterministic_metrics=deterministic_metrics,
                rubric_results=rubric_results_for_results_json,
                judge_disagreements=judge_disagreements,
                artifact_paths=artifact_paths,
                execution_stats=execution_stats_for_output
            )
            self._log(f"✓ Wrote {results_path}")
            
        except OutputWriteError:
            # Re-raise OutputWriteError without wrapping to preserve original message
            raise
        except Exception as e:
            raise OutputWriteError(f"Output writing failed: {e}") from e
    
    def _handle_report_lifecycle(self, run_id: str) -> Tuple[Optional[str], str]:
        """
        Generate HTML report and persist report metadata to results.json.
        
        Encapsulates the full Step 11 lifecycle:
        1. Generate report (or skip if configured)
        2. Persist report path and status to results.json
        3. Emit degraded-state warnings if metadata persistence fails
        
        Args:
            run_id: Run identifier
            
        Returns:
            Tuple of (report_path, report_generation_status)
        """
        if self.skip_report:
            self._log("\nStep 11: Skipping HTML report generation (--skip-report flag set)", force=True)
            if not self._update_results_with_report(None, "skipped"):
                self._log("⚠ Warning: results.json metadata may be incomplete (skipped status not persisted)")
            return None, "skipped"
        
        # Import once for the except branch below.
        from agent_eval.evaluators.trace_eval.reporting.report_builder import ReportGenerationError as _ReportGenerationError

        self._log("\nStep 11: Generating HTML report", force=True)
        try:
            report_path = self._generate_html_report(run_id)
            self._log(f"✓ Generated HTML report: {report_path}")
            
            if not self._update_results_with_report(report_path, "success"):
                self._log("⚠ Warning: results.json metadata may be incomplete (report info not persisted)")
            
            return report_path, "success"
            
        except (FileNotFoundError, OSError) as e:
            # Pre-flight artifact missing or file system error — operational failure
            self._log(f"⚠ Warning: HTML report generation failed: {e}")
            
            if not self._update_results_with_report(None, "failed"):
                self._log("⚠ Warning: results.json metadata may be incomplete (failure status not persisted)")
            
            if self.debug:
                import traceback
                traceback.print_exc()
            
            return None, "failed"
            
        except _ReportGenerationError as e:
            # Report-layer error — degrade gracefully.
            self._log(f"⚠ Warning: HTML report generation failed: {e}")
            
            if not self._update_results_with_report(None, "failed"):
                self._log("⚠ Warning: results.json metadata may be incomplete (failure status not persisted)")
            
            if self.debug:
                import traceback
                traceback.print_exc()
            
            return None, "failed"

        except Exception as e:
            # Not a known report-layer error — likely a programmer bug in
            # runner/report glue code.  Still degrade gracefully (evaluation
            # artifacts are already written) but log at higher severity.
            self._log(f"⚠ Warning: Unexpected error during report generation (may be a bug): {e}")
            
            if not self._update_results_with_report(None, "failed"):
                self._log("⚠ Warning: results.json metadata may be incomplete (failure status not persisted)")
            
            if self.debug:
                import traceback
                traceback.print_exc()
            
            return None, "failed"
    
    def run(self) -> int:
        """
        Run complete trace evaluation flow.
        
        ARCHITECTURE: TraceEvaluator only accepts normalized input.
        Input must be a valid NormalizedRun JSON file.
        
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        start_time = time.time()
        
        try:
            self._log("=" * 60, force=True)
            self._log("TRACE EVALUATOR", force=True)
            self._log("=" * 60, force=True)
            
            # Step 1: Load normalized input
            self._log(f"\nStep 1: Loading NormalizedRun from {self.input_path}", force=True)
            with open(self.input_path, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            
            # Step 2: Validate input
            self._log("\nStep 2: Validating input", force=True)
            validated_input = self._validate_input(input_data)
            run_id = validated_input.get("run_id")
            
            # Ensure run_id is present and stable.
            # The UUID suffix mirrors the pipeline's fallback format so that
            # runner-direct and pipeline-driven runs produce equally unique IDs.
            if not run_id:
                run_id = f"run_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
                self._log(f"⚠ Warning: No run_id in input, generated: {run_id}")
                validated_input["run_id"] = run_id
            
            # NOTE: Normalized artifact persistence is owned by the pipeline layer.
            # Runner does not write normalized_run.json — it only consumes it.
            
            # Step 3: Compute deterministic metrics
            self._log("\nStep 3: Computing deterministic metrics", force=True)
            deterministic_metrics = self._compute_deterministic_metrics(validated_input)
            
            # Step 4: Load rubrics
            self._log("\nStep 4: Loading rubrics", force=True)
            rubrics = self._load_rubrics()
            
            # Step 5: Load judge configuration
            self._log("\nStep 5: Loading judge configuration", force=True)
            judge_config = self._load_judge_config()
            
            # Step 6: Build judge clients
            self._log("\nStep 6: Building judge clients", force=True)
            judge_clients = self._build_judge_clients(judge_config)
            
            # Step 7: Build JudgeJobs
            self._log("\nStep 7: Building JudgeJobs", force=True)
            jobs = self._build_judge_jobs(
                normalized_run=validated_input,
                rubrics=rubrics,
                judge_config=judge_config,
                deterministic_metrics=deterministic_metrics
            )
            
            # Step 8: Execute jobs
            self._log("\nStep 8: Executing JudgeJobs", force=True)
            execution_stats = self._execute_jobs(jobs, judge_clients)
            
            # Step 9: Aggregate results
            self._log("\nStep 9: Aggregating results", force=True)
            judge_runs_path = self.output_dir / "judge_runs.jsonl"
            aggregated_results = self._aggregate_results(judge_runs_path, rubrics, run_id)
            
            if "aggregation_stats" in aggregated_results:
                execution_stats["aggregation_stats"] = aggregated_results["aggregation_stats"]
            
            if "judge_summary" in aggregated_results and "total_jobs" in execution_stats:
                aggregated_results["judge_summary"]["attempted_jobs_total"] = execution_stats["total_jobs"]
            
            # Step 10: Write outputs FIRST (trace_eval.json, results.json)
            # This ensures all canonical artifacts exist before report generation
            self._log("\nStep 10: Writing output files", force=True)
            self._write_outputs(
                run_id=run_id,
                deterministic_metrics=deterministic_metrics,
                aggregated_results=aggregated_results,
                execution_stats=execution_stats,
                rubrics=rubrics,
                judge_config=judge_config,
                normalized_run=validated_input,
                report_path=None,  # Will be updated after report generation
                report_generation_status="pending"
            )
            
            # Step 11: Generate HTML report AFTER outputs
            # Depends on trace_eval.json and results.json existing with the expected schema.
            # generate_report() reads these artifacts directly from output_dir.
            report_path, report_generation_status = self._handle_report_lifecycle(run_id)
            
            # Success summary
            elapsed_time = time.time() - start_time
            self._log("\n" + "=" * 60, force=True)
            self._log(f"✓ EVALUATION COMPLETE", force=True)
            self._log(f"  Run ID: {run_id}", force=True)
            self._log(f"  Output directory: {self.output_dir}", force=True)
            if report_generation_status == "success" and report_path:
                self._log(f"  HTML report: {report_path}", force=True)
            self._log(f"  Elapsed time: {elapsed_time:.2f}s", force=True)
            self._log("=" * 60, force=True)
            
            return 0
            
        except InputValidationError as e:
            self._log(f"\n✗ Input validation error: {e}", force=True)
            if self.debug:
                import traceback
                traceback.print_exc()
            return getattr(e, 'EXIT_CODE', 3)
        except ConfigError as e:
            self._log(f"\n✗ Configuration error: {e}", force=True)
            if self.debug:
                import traceback
                traceback.print_exc()
            return getattr(e, 'EXIT_CODE', 2)
        except AdapterError as e:
            self._log(f"\n✗ Adapter error: {e}", force=True)
            if self.debug:
                import traceback
                traceback.print_exc()
            return getattr(e, 'EXIT_CODE', 4)
        except AggregationError as e:
            self._log(f"\n✗ Aggregation error: {e}", force=True)
            if self.debug:
                import traceback
                traceback.print_exc()
            return getattr(e, 'EXIT_CODE', 5)
        except OutputWriteError as e:
            self._log(f"\n✗ Output writing error: {e}", force=True)
            if self.debug:
                import traceback
                traceback.print_exc()
            return getattr(e, 'EXIT_CODE', 6)
        except TraceEvaluatorError as e:
            self._log(f"\n✗ Error: {e}", force=True)
            if self.debug:
                import traceback
                traceback.print_exc()
            return getattr(e, 'EXIT_CODE', 1)
        except Exception as e:
            self._log(f"\n✗ Unexpected error: {e}", force=True)
            if self.debug or self.verbose:
                import traceback
                traceback.print_exc()
            return 1
