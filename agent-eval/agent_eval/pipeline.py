"""
Pipeline orchestrator for end-to-end trace evaluation.

This module provides a unified pipeline that:
1. Detects if input is raw or normalized format using schema validation
2. Runs Generic_JSON_Adapter if needed
3. Validates adapter output against NormalizedRun schema
4. Persists normalized artifact with safe filenames
5. Calls TraceEvaluator with normalized input
6. Returns evaluation results

ARCHITECTURE: Pipeline is the single source of truth for:
- Input format detection (via schema validation)
- Adapter invocation and output validation
- Normalized artifact persistence (runner does NOT write normalized artifacts)
"""

import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from agent_eval.evaluators.trace_eval.filename_utils import sanitize_filename


class PipelineError(Exception):
    """Pipeline execution error.

    Every instance carries an ``exit_code`` that the CLI layer can use
    directly — no message-text parsing required.  Subclasses set a
    different default via ``_default_exit_code``.

    Attributes:
        exit_code: Process exit code the CLI should return for this error.
    """
    _default_exit_code: int = 1  # EXIT_RUNTIME_ERROR

    def __init__(self, message: str, exit_code: int | None = None):
        super().__init__(message)
        self.exit_code: int = (
            exit_code if exit_code is not None else self._default_exit_code
        )


class PipelineValidationError(PipelineError):
    """Input data failed validation (malformed JSON, schema mismatch)."""
    _default_exit_code: int = 4  # EXIT_VALIDATION_ERROR


class PipelineConfigError(PipelineError):
    """Setup / configuration problem (missing schema, import failure)."""
    _default_exit_code: int = 3  # EXIT_CONFIG_ERROR


class AdapterExecutionError(PipelineError):
    """Raised when the Generic_JSON_Adapter fails."""
    _default_exit_code: int = 1  # EXIT_RUNTIME_ERROR


def detect_input_format(input_path: str) -> str:
    """
    Detect if input is raw or normalized format using schema validation.

    Uses InputValidator to perform proper schema validation instead of
    heuristic field checking. This ensures we correctly identify normalized
    inputs and don't accidentally treat malformed normalized files as raw.

    Args:
        input_path: Path to input file

    Returns:
        "normalized" if input passes NormalizedRun schema validation, "raw" otherwise

    Raises:
        PipelineError: If critical errors occur (invalid JSON, missing schema,
            import failures, etc.)
    """
    try:
        from agent_eval.evaluators.trace_eval.input_validator import (
            InputValidator,
            ValidationError as InputValidationError,
        )

        # Load JSON data
        data: dict | None = None
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Attempt schema validation
        validator = InputValidator()
        validator.validate(data)

        # If validation passes, it's normalized
        return "normalized"

    except InputValidationError:
        # Schema validation failed.  Distinguish between a genuine raw trace
        # and a broken "almost-normalized" file.  If the data carries at least
        # two of the four required normalized top-level keys it is almost
        # certainly a failed normalization attempt, not a raw trace.  Fail
        # early instead of silently routing it into the adapter path.
        #
        # KNOWN LIMITATION: This is a heuristic, not a strict detection model.
        # A malformed normalized file that retains only one surviving
        # normalized key will still be classified as "raw" and routed to the
        # adapter.  The threshold of 2 balances false-positive risk (flagging
        # genuine raw traces that happen to use "metadata") against
        # false-negative risk (silently re-adapting broken normalized files).
        _NORMALIZED_KEYS = {"run_id", "metadata", "adapter_stats", "turns"}
        if isinstance(data, dict) and len(_NORMALIZED_KEYS & data.keys()) >= 2:
            raise PipelineValidationError(
                f"Input appears to be a normalized file but failed schema "
                f"validation: {input_path}.  Fix the file or re-run the "
                f"adapter on the original raw trace."
            )
        return "raw"
    except json.JSONDecodeError as e:
        # Invalid JSON should not silently become "raw" — it hides broken files
        # and defers the failure into adapter code where the error is confusing.
        raise PipelineValidationError(
            f"Input file contains malformed JSON: {input_path}: {e}"
        ) from e
    except (ImportError, FileNotFoundError, AttributeError) as e:
        # Critical errors that should not be hidden:
        # - ImportError: validator module or dependencies missing
        # - FileNotFoundError: schema file missing
        # - AttributeError: validator API changed
        raise PipelineConfigError(
            f"Critical error during input format detection: {e}. "
            f"This indicates a setup or configuration problem, not a raw input file."
        ) from e
    except Exception as e:
        # Unexpected errors should also surface
        raise PipelineError(
            f"Unexpected error during input format detection: {e}"
        ) from e


def run_pipeline(
    input_path: str,
    judge_config_path: str,
    output_dir: str,
    adapter_config_path: Optional[str] = None,
    rubrics_path: Optional[str] = None,
    verbose: bool = False,
    debug: bool = False,
    skip_report: bool = False,
    enable_charts: bool = True
) -> Dict[str, Any]:
    """
    Run complete evaluation pipeline.

    ARCHITECTURE: Pipeline is the single source of truth for:
    - Input format detection (via schema validation)
    - Adapter invocation and output validation
    - Normalized artifact persistence (runner does NOT write normalized artifacts)

    TraceEvaluator only accepts pre-validated normalized input.

    Args:
        input_path: Path to raw trace or NormalizedRun file
        judge_config_path: Path to judges.yaml configuration
        output_dir: Directory for output files
        adapter_config_path: Optional path to adapter configuration
        rubrics_path: Optional path to user rubrics.yaml
        verbose: Enable verbose output
        debug: Enable debug mode
        skip_report: Skip HTML report generation
        enable_charts: Enable chart generation in HTML reports (default: True)

    Returns:
        Pipeline execution results with:
        - input_format: "raw" or "normalized"
        - normalized_path: Path to normalized artifact
        - evaluation_exit_code: Exit code from TraceEvaluator
        - output_dir: Output directory path
        - success: True if exit code is 0
        - run_id: The run identifier used
        - trace_eval_path: Path to trace_eval.json (None if file does not exist)
        - results_path: Path to results.json (None if file does not exist)
        - report_path: Path to report.html (None if file does not exist)

    Note:
        trace_eval_path, results_path, and report_path are reported whenever
        the files exist on disk, even if evaluation failed (exit_code != 0).
        Callers should check the ``success`` field to determine if artifacts
        are complete.

    Raises:
        PipelineError: If pipeline execution fails
        AdapterExecutionError: If Generic_JSON_Adapter fails
    """
    try:
        from agent_eval.evaluators.trace_eval.runner import TraceEvaluator
        from agent_eval.evaluators.trace_eval.json_utils import SafeJSONEncoder, validation_error_message
        from agent_eval.adapters.generic_json.adapter import adapt
        from agent_eval.adapters.generic_json.exceptions import AdapterError as _AdapterError
        from agent_eval.evaluators.trace_eval.input_validator import InputValidator, ValidationError

        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        if verbose:
            print("=" * 60)
            print("EVALUATION PIPELINE")
            print("=" * 60)

        # Step 1: Detect input format using schema validation
        input_format = detect_input_format(input_path)

        if verbose:
            print(f"\nStep 1: Detected input format: {input_format}")

        # Step 2: Normalize input if needed
        if input_format == "raw":
            if verbose:
                print(f"\nStep 2: Running Generic_JSON_Adapter on {input_path}")

            # Run adapter — catch adapter-layer errors specifically.
            # AdapterError is the adapter's own base exception; letting
            # unexpected programming bugs (e.g. AttributeError, TypeError)
            # propagate avoids hiding them under a runtime wrapper.
            #
            # NOTE: If the adapter leaks an OSError or ValueError instead of
            # wrapping it in AdapterError, the exception will bypass this
            # branch and land in the outer pipeline catch.  This is defensible
            # (the outer catch produces a clear PipelineError) but means the
            # caller won't see an AdapterExecutionError for those cases.
            try:
                normalized_data = adapt(
                    path=input_path,
                    config_path=adapter_config_path
                )
            except _AdapterError as e:
                raise AdapterExecutionError(
                    f"Generic_JSON_Adapter failed on {input_path}: {e}"
                ) from e

            # Validate adapter output against NormalizedRun schema
            if verbose:
                print("  Validating adapter output against schema...")

            validator = InputValidator()
            try:
                validated_data = validator.validate(normalized_data)
            except ValidationError as e:
                raise PipelineValidationError(
                    f"Adapter output failed schema validation: {validation_error_message(e)}"
                ) from e

            if verbose:
                print("  ✓ Adapter output validated")

        else:
            if verbose:
                print(f"\nStep 2: Input already normalized, validating and persisting to output directory")

            # Load and validate the normalized input
            with open(input_path, 'r', encoding='utf-8') as f:
                normalized_data = json.load(f)

            # Validate to ensure it's truly normalized
            validator = InputValidator()
            try:
                validated_data = validator.validate(normalized_data)
            except ValidationError as e:
                raise PipelineValidationError(
                    f"Input claimed to be normalized but failed validation: {validation_error_message(e)}"
                ) from e

        # Resolve run_id with fallback.  When the pipeline generates a
        # fallback ID the suffix includes a short UUID fragment so concurrent
        # runs targeting the same output directory do not collide on the
        # normalized artifact filename.  Caller-supplied run_ids are used
        # as-is; if two runs share the same run_id the later write wins.
        run_id = validated_data.get("run_id")
        if not run_id:
            run_id = f"run_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
            validated_data["run_id"] = run_id
            if verbose:
                print(f"  ⚠ No run_id in input, generated: {run_id}")

        # Pipeline owns normalized artifact persistence
        safe_run_id = sanitize_filename(run_id)
        normalized_path = output_path / f"normalized_run.{safe_run_id}.json"

        with open(normalized_path, 'w', encoding='utf-8') as f:
            json.dump(validated_data, f, ensure_ascii=False, indent=2, cls=SafeJSONEncoder)

        if verbose:
            print(f"✓ Wrote canonical normalized artifact: {normalized_path}")

        # Use canonical normalized artifact as input for evaluator
        evaluator_input = str(normalized_path)

        # Step 3: Run TraceEvaluator in normalized-only mode
        # Pipeline owns adaptation — runner only accepts normalized input
        if verbose:
            print(f"\nStep 3: Running TraceEvaluator (normalized-only mode)")

        evaluator = TraceEvaluator(
            input_path=evaluator_input,
            judge_config_path=judge_config_path,
            output_dir=str(output_path),
            rubrics_path=rubrics_path,
            verbose=verbose,
            debug=debug,
            skip_report=skip_report,
            enable_charts=enable_charts
        )

        exit_code = evaluator.run()

        # Step 4: Build enriched result payload
        trace_eval_path = output_path / "trace_eval.json"
        results_json_path = output_path / "results.json"
        report_html_path = output_path / "report.html"

        results = {
            "input_format": input_format,
            "normalized_path": str(normalized_path),
            "evaluation_exit_code": exit_code,
            "output_dir": str(output_path),
            "success": exit_code == 0,
            "run_id": run_id,
            "trace_eval_path": str(trace_eval_path) if trace_eval_path.exists() else None,
            "results_path": str(results_json_path) if results_json_path.exists() else None,
            "report_path": str(report_html_path) if report_html_path.exists() else None,
        }

        if verbose:
            print("\n" + "=" * 60)
            if results["success"]:
                print("✓ PIPELINE COMPLETE")
            else:
                print(f"✗ PIPELINE FAILED (exit code: {exit_code})")
            print(f"  Output directory: {output_path}")
            print("=" * 60)

        return results

    except PipelineError:
        # Re-raise without wrapping (AdapterExecutionError is a subclass)
        raise
    except (OSError, RuntimeError, ValueError) as e:
        # Operational failures that can reasonably occur at runtime.
        # Programming bugs (AttributeError, TypeError, KeyError, etc.) are
        # NOT caught here so they surface directly during development.
        raise PipelineError(f"Pipeline execution failed: {e}") from e
