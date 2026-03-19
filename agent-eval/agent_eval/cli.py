"""CLI entry point for agentic-eval."""

import argparse
import os
import sys
from pathlib import Path


# Exit codes — ordered by severity (higher = more severe for priority logic)
EXIT_SUCCESS = 0
EXIT_RUNTIME_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_CONFIG_ERROR = 3
EXIT_VALIDATION_ERROR = 4

# Priority ranking for exit codes when multiple validation errors
# accumulate.  Higher rank = more severe; the most severe wins.
_EXIT_CODE_SEVERITY = {
    EXIT_USAGE_ERROR: 0,
    EXIT_CONFIG_ERROR: 1,
    EXIT_VALIDATION_ERROR: 2,
}


class CLIValidationError(Exception):
    """Raised when CLI argument validation fails.

    Attributes:
        exit_code: Suggested process exit code for this class of error.
        errors: List of human-readable validation messages.
    """

    def __init__(self, errors: list[str], exit_code: int = EXIT_USAGE_ERROR):
        self.errors = errors
        self.exit_code = exit_code
        super().__init__("; ".join(errors))


def _more_severe(current: int, candidate: int) -> int:
    """Return whichever exit code has higher severity."""
    if _EXIT_CODE_SEVERITY.get(candidate, -1) > _EXIT_CODE_SEVERITY.get(current, -1):
        return candidate
    return current


def validate_cli_args(args: argparse.Namespace) -> None:
    """
    Validate CLI arguments before execution.

    Checks only the attributes that actually exist on *args*, so the
    function is reusable across different parsers without assuming a
    fixed set of flags.

    When multiple errors are found the exit code reflects the most
    severe category (validation > config > usage).

    On success, ``args.output_dir`` is resolved to an absolute path.
    On failure the namespace is not mutated.

    Args:
        args: Parsed CLI arguments

    Raises:
        CLIValidationError: If any validation check fails.
    """
    errors: list[str] = []
    exit_code = EXIT_USAGE_ERROR
    resolved_output_dir: str | None = None

    # Validate --input exists and is readable
    if hasattr(args, "input"):
        if not os.path.exists(args.input):
            errors.append(f"Input file not found: {args.input}")
            exit_code = _more_severe(exit_code, EXIT_VALIDATION_ERROR)
        elif not os.path.isfile(args.input):
            errors.append(f"Input path is not a file: {args.input}")
            exit_code = _more_severe(exit_code, EXIT_VALIDATION_ERROR)
        elif not os.access(args.input, os.R_OK):
            errors.append(f"Input file not readable: {args.input}")
            exit_code = _more_severe(exit_code, EXIT_VALIDATION_ERROR)

    # Validate --judge-config exists and is readable (config error)
    if hasattr(args, "judge_config"):
        if not os.path.exists(args.judge_config):
            errors.append(f"Judge config file not found: {args.judge_config}")
            exit_code = _more_severe(exit_code, EXIT_CONFIG_ERROR)
        elif not os.path.isfile(args.judge_config):
            errors.append(f"Judge config path is not a file: {args.judge_config}")
            exit_code = _more_severe(exit_code, EXIT_CONFIG_ERROR)
        elif not os.access(args.judge_config, os.R_OK):
            errors.append(f"Judge config file not readable: {args.judge_config}")
            exit_code = _more_severe(exit_code, EXIT_CONFIG_ERROR)

    # Validate --rubrics exists if provided (config error)
    rubrics = getattr(args, "rubrics", None)
    if rubrics:
        if not os.path.exists(rubrics):
            errors.append(f"Rubrics file not found: {rubrics}")
            exit_code = _more_severe(exit_code, EXIT_CONFIG_ERROR)
        elif not os.path.isfile(rubrics):
            errors.append(f"Rubrics path is not a file: {rubrics}")
            exit_code = _more_severe(exit_code, EXIT_CONFIG_ERROR)
        elif not os.access(rubrics, os.R_OK):
            errors.append(f"Rubrics file not readable: {rubrics}")
            exit_code = _more_severe(exit_code, EXIT_CONFIG_ERROR)

    # Validate --output-dir is writable (usage error)
    if hasattr(args, "output_dir"):
        output_path = Path(args.output_dir).resolve()
        resolved_output_dir = str(output_path)
        if output_path.exists():
            if not output_path.is_dir():
                errors.append(f"Output path exists but is not a directory: {args.output_dir}")
                exit_code = _more_severe(exit_code, EXIT_USAGE_ERROR)
            else:
                try:
                    test_file = output_path / f".write_test_{os.getpid()}"
                    test_file.touch()
                    test_file.unlink()
                except OSError as e:
                    errors.append(
                        f"Output directory not writable (touch test failed): {args.output_dir} - {e}"
                    )
                    exit_code = _more_severe(exit_code, EXIT_USAGE_ERROR)
        else:
            parent = output_path.parent
            if not parent.exists():
                errors.append(f"Parent directory does not exist: {parent}")
                exit_code = _more_severe(exit_code, EXIT_USAGE_ERROR)
            elif not os.access(str(parent), os.W_OK):
                errors.append(f"Cannot create output directory (parent not writable): {parent}")
                exit_code = _more_severe(exit_code, EXIT_USAGE_ERROR)
            elif not os.access(str(parent), os.X_OK):
                errors.append(
                    f"Cannot create output directory (parent not executable/searchable): {parent}"
                )
                exit_code = _more_severe(exit_code, EXIT_USAGE_ERROR)

    if errors:
        raise CLIValidationError(errors, exit_code)

    # Mutate only after validation succeeds
    if resolved_output_dir is not None:
        args.output_dir = resolved_output_dir


def _handle_validation_error(e: CLIValidationError) -> int:
    """Print validation errors to stderr and return the appropriate exit code."""
    print("CLI validation errors:", file=sys.stderr)
    for error in e.errors:
        print(f"  - {error}", file=sys.stderr)
    return e.exit_code


def _run_via_pipeline(args: argparse.Namespace) -> int:
    """
    Shared helper: delegates to run_pipeline() — the single source of truth
    for input detection, adapter invocation, normalization, and evaluator handoff.

    Exit-code mapping reads the ``exit_code`` instance attribute that every
    PipelineError carries (set in ``__init__``, not a class-level annotation).

    Args:
        args: Parsed CLI namespace (must have input, judge_config, output_dir;
              may have adapter_config, rubrics, verbose, debug, skip_report,
              enable_charts).

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        from agent_eval.pipeline import run_pipeline, PipelineError

        results = run_pipeline(
            input_path=args.input,
            judge_config_path=args.judge_config,
            output_dir=args.output_dir,
            adapter_config_path=getattr(args, "adapter_config", None),
            rubrics_path=getattr(args, "rubrics", None),
            verbose=getattr(args, "verbose", False),
            debug=getattr(args, "debug", False),
            skip_report=getattr(args, "skip_report", False),
            enable_charts=getattr(args, "enable_charts", True),
        )

        return results.get("evaluation_exit_code", EXIT_RUNTIME_ERROR)

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return EXIT_RUNTIME_ERROR

    except PipelineError as e:
        print(f"Pipeline error: {e}", file=sys.stderr)
        if getattr(args, "debug", False):
            import traceback
            traceback.print_exc()
        # PipelineError.__init__ guarantees exit_code, but getattr
        # provides a safety net against future subclasses that bypass it.
        return getattr(e, "exit_code", EXIT_RUNTIME_ERROR)

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if getattr(args, "debug", False):
            import traceback
            traceback.print_exc()
        return EXIT_RUNTIME_ERROR


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments shared by both CLI entrypoints."""
    parser.add_argument(
        "--input",
        required=True,
        metavar="PATH",
        help="Path to input file (raw trace or NormalizedRun JSON). "
             "Format is auto-detected by the pipeline."
    )
    parser.add_argument(
        "--judge-config",
        required=True,
        metavar="PATH",
        help="Path to judges.yaml configuration file (1-5 judges required)"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        metavar="DIR",
        help="Directory for output files (normalized_run.json, trace_eval.json, "
             "judge_runs.jsonl, results.json)"
    )
    parser.add_argument(
        "--adapter-config",
        metavar="PATH",
        help="Path to adapter configuration (optional, for raw trace processing)"
    )
    parser.add_argument(
        "--rubrics",
        metavar="PATH",
        help="Path to user rubrics.yaml (optional, merges with default rubrics by rubric_id)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output with detailed progress information"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with full stack traces on errors"
    )
    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="Skip HTML report generation (Step 11)"
    )
    parser.add_argument(
        "--no-charts",
        action="store_false",
        dest="enable_charts",
        help="Disable chart generation in HTML reports (charts enabled by default)"
    )
    parser.set_defaults(enable_charts=True)


def trace_eval_cli(argv=None):
    """
    Legacy CLI entrypoint for trace evaluation.

    Delegates to run_pipeline() so there is a single orchestration path.
    Kept for backward compatibility; ``eval_pipeline_cli()`` is the
    preferred entrypoint and is what ``main()`` routes to.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:] if None)

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        prog="trace-eval",
        description="Evaluate agent traces using rubric-driven multi-judge system "
                    "(legacy alias — prefer eval-pipeline)",
        epilog="Part of the agent-evaluation framework"
    )
    _add_common_arguments(parser)
    args = parser.parse_args(argv)

    try:
        validate_cli_args(args)
    except CLIValidationError as e:
        return _handle_validation_error(e)

    return _run_via_pipeline(args)


def eval_pipeline_cli(argv=None):
    """
    CLI entrypoint for full evaluation pipeline.

    Automatically detects input format (raw vs normalized) and runs
    the complete pipeline: adapter (if needed) → evaluator → results.

    This is the preferred CLI path. ``run_pipeline()`` is the single
    source of truth for orchestration.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:] if None)

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        prog="eval-pipeline",
        description="Run complete evaluation pipeline with automatic format detection",
        epilog="Part of the agent-evaluation framework"
    )
    _add_common_arguments(parser)
    args = parser.parse_args(argv)

    try:
        validate_cli_args(args)
    except CLIValidationError as e:
        return _handle_validation_error(e)

    return _run_via_pipeline(args)


def main(argv=None):
    """
    Main CLI entry point.

    Routes to eval_pipeline_cli — the preferred pipeline-based path.
    ``trace_eval_cli`` is kept for backward compatibility but also
    delegates to ``run_pipeline()`` internally.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:] if None)

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    return eval_pipeline_cli(argv)


if __name__ == "__main__":
    sys.exit(main())
