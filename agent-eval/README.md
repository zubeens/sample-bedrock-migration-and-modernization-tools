# Agent Evaluation Framework

Evaluate agent behavior and response quality from recorded execution traces without re-running the agent runtime.

This framework enables offline evaluation of agent traces for debugging, benchmarking, regression testing, and CI pipelines. It normalizes raw trace data into a standard schema, computes deterministic metrics, runs rubric-based judges, and produces structured evaluation artifacts.

## Overview

Modern agent systems generate rich execution traces containing user queries, model responses, tool calls, and reasoning steps. Evaluating agent quality often requires re-running the full agent runtime, which is slow, expensive, and difficult to integrate into CI workflows.

This framework evaluates existing traces instead of re-running agents, enabling fast and reproducible evaluation.

**Key capabilities:**
- Evaluate previously recorded agent traces
- Compute deterministic execution metrics
- Score traces using rubric-based judges
- Support mock or real LLM judges
- Run judge evaluations in parallel
- Generate structured evaluation artifacts

## Key Features

### Trace-based evaluation

Evaluate agent behavior directly from recorded execution traces.

### Framework-agnostic

Works with traces exported from:
- Custom agent runtimes
- OpenTelemetry pipelines
- CloudWatch logs
- AgentCore observability data

### Deterministic + LLM evaluation

Combines:
- Deterministic metrics (computed from trace structure)
- LLM-based rubric scoring (semantic evaluation)

### Parallel judge evaluation

Multiple judges can run simultaneously across rubrics.

### Fault-tolerant execution

Evaluation artifacts are always generated even if optional steps (such as HTML report generation) fail.

### Config-driven

Evaluation behavior is controlled by configuration files:
- `judges.yaml`
- `rubrics.yaml`

## Quick Start

Run the evaluator using the included sample trace:

```bash
python -m agent_eval.cli \
  --input test-fixtures/baseline/good_001_direct_answer.json \
  --judge-config test-fixtures/baseline/judges.mock.yaml \
  --rubrics test-fixtures/baseline/rubrics.test.yaml \
  --output-dir ./output
```

### Input Modes

The CLI accepts both:
- **Raw traces** → automatically normalized via Generic JSON Adapter
- **NormalizedRun JSON** → directly evaluated (adapter skipped)

The pipeline detects input type automatically.

When `--rubrics` is omitted, built-in defaults are used:

```bash
python -m agent_eval.cli \
  --input test-fixtures/baseline/good_001_direct_answer.json \
  --judge-config test-fixtures/baseline/judges.mock.yaml \
  --output-dir ./output
```

### Output

```
output/
  ├── results.json
  ├── trace_eval.json
  ├── judge_runs.jsonl
  ├── normalized_run.<run_id>.json
  └── report_<run_id>.html
```

Some artifacts are conditional depending on input mode and report settings.

### Artifact descriptions

| File | Description |
|------|-------------|
| `results.json` | Final aggregated evaluation output with config hashes and artifact checksums |
| `trace_eval.json` | Detailed metrics and rubric results |
| `judge_runs.jsonl` | Raw judge responses |
| `normalized_run.*.json` | Normalized trace (only generated when input is raw) |
| `report_<run_id>.html` | Interactive HTML report (optional, non-blocking) |

### HTML Report

An interactive HTML report is generated after evaluation.

- Non-blocking: evaluation succeeds even if report generation fails
- Generated unless `--skip-report` is provided
- Includes metrics, rubric scores, evidence, and diagnostics
- Stored as `report_<run_id>.html` in output directory

To skip report generation:

```bash
python -m agent_eval.cli \
  --input trace.json \
  --judge-config judges.yaml \
  --rubrics rubrics.yaml \
  --output-dir ./output \
  --skip-report
```

To generate a report without charts (useful for faster output or environments without chart dependencies):

```bash
python -m agent_eval.cli \
  --input trace.json \
  --judge-config judges.yaml \
  --rubrics rubrics.yaml \
  --output-dir ./output \
  --no-charts
```

To generate reports from existing artifacts:

```python
from agent_eval.evaluators.trace_eval.reporting import generate_report

report_path = generate_report(
    output_dir="./output",
    run_id="my_run",
    enable_charts=True
)
```

For report structure, performance, and troubleshooting details, see [guides/HTML_REPORT_USER_GUIDE.md](guides/HTML_REPORT_USER_GUIDE.md).

## CLI Usage

The framework provides a unified CLI for running the full evaluation pipeline. The CLI uses a single command interface (no subcommands).

### Pipeline Contract

```
Input → Adapter (if raw) → Evaluator → Artifacts → (Optional) Report
```

### Supported flags

| Flag | Required | Description |
|------|----------|-------------|
| `--input` | Yes | Path to input file (raw trace or NormalizedRun JSON) |
| `--judge-config` | Yes | Path to judges.yaml configuration |
| `--output-dir` | Yes | Directory for output files |
| `--rubrics` | No | Path to user rubrics.yaml (optional; defaults are used if not provided) |
| `--adapter-config` | No | Path to adapter configuration (for raw trace processing) |
| `--skip-report` | No | Skip HTML report generation |
| `--no-charts` | No | Disable chart generation in HTML reports |
| `--verbose` | No | Enable verbose output |
| `--debug` | No | Enable debug mode with full stack traces |

### Validate CLI setup

```bash
python -m agent_eval.cli --help
```

## How It Works

The framework follows a simple pipeline:

```
Input (raw or normalized)
      ↓
Normalization (if raw)
      ↓
NormalizedRun
      ↓
Trace Evaluator
  • deterministic metrics
  • rubric-based judge scoring
      ↓
Artifacts
      ↓
(Optional) Report
```

### Deterministic metrics

Computed directly from trace structure.

Examples:
- Turn counts
- Tool call statistics
- Tool success rate
- Latency metrics

### Judge-based evaluation

Rubric-based scoring using extracted trace evidence.

Examples:
- Answer correctness
- Reasoning quality
- Tool usage quality
- Groundedness
- Safety checks

## Installation

Requires Python 3.11+

```bash
git clone https://github.com/<org>/agent-eval.git
cd agent-eval
pip install -e .
```

## Judge Configuration

The framework supports two judge types:

| Mode | Description |
|------|-------------|
| Mock judges | Deterministic responses for testing |
| Real judges | LLM-based evaluation |

The quick start uses mock judges so the pipeline can run without external APIs.

### Example real judge configuration

```yaml
judges:
  - judge_id: judge_1
    provider: bedrock
    model_id: anthropic.claude-3-sonnet-20240229-v1:0
    params:
      temperature: 0.0
      max_tokens: 1000
```

Run evaluation with:

```bash
python -m agent_eval.cli \
  --input trace.json \
  --judge-config judges.yaml \
  --rubrics rubrics.yaml \
  --output-dir ./output
```

Typical setups use 1–5 judges for comparison and disagreement detection.

## Rubrics

Evaluation behavior is defined by rubric configuration.

Each rubric specifies:
- Evaluation scope
- Evidence selectors
- Scoring scale
- Judge instructions

Rubrics can override built-in defaults or add new evaluation criteria.

Changing the rubric configuration changes evaluation behavior without modifying application code.

### Rubric Scope

Rubrics can evaluate either individual turns or the entire conversation run.

**Turn scope**

Evaluates a single turn independently. Selectors operate on a single turn object.

Example selectors:
```
$.user_query
$.steps[?(@.kind=='TOOL_CALL')]
$.final_answer
```

**Run scope**

Evaluates the full trace. Selectors can reference all turns.

Example selectors:
```
$.turns[*].user_query
$.turns[*].steps
$.turns[*].final_answer
```

**Rule of thumb:**

| Scope | Selector style |
|-------|----------------|
| `turn` | `$.user_query` |
| `run` | `$.turns[*].user_query` |

Using run-level selectors with turn scope will return no evidence because the context is narrowed to the individual turn.

## Judge Execution Model

Judge evaluations run in parallel:

```
Rubric × Judge jobs
        ↓
Queue runner
        ↓
Parallel execution
        ↓
Score aggregation
```

### Aggregation behavior

The evaluator aggregates the judge results it receives.

**Within-judge aggregation:**

If repeated samples exist:
- Numeric rubrics → median, mean, variance
- Categorical rubrics → majority vote

**Cross-judge aggregation:**

Across multiple judges:
```
weighted_average = sample_size / (1 + variance)
```

This allows stable judges to influence the final score more strongly.

## Trace Input

The framework can evaluate:
- Raw trace JSON
- Normalized traces (NormalizedRun)

### Minimal trace fields

Raw traces should include:
- `timestamp`
- `event_type`
- `text` or tool metadata
- `session_id`

Example:

```json
{
  "events": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "event_type": "user_message",
      "text": "What is the refund policy?",
      "session_id": "session-123"
    }
  ]
}
```

## Generic JSON Adapter

The Generic JSON Adapter converts arbitrary trace formats into the NormalizedRun schema.

**Configuration:**
```
agent_eval/adapters/generic_json/adapter_config.yaml
```

**Responsibilities:**
- Field alias mapping
- Turn segmentation
- Tool call/result linking
- Confidence scoring

**Example:**

```python
from agent_eval.adapters.generic_json import adapt

normalized = adapt("trace.json")
print(len(normalized["turns"]))
```

### Debugging Adapter Behavior

To inspect how raw traces were normalized:

```bash
python -m agent_eval.tools.inspect_adapter_stages trace.json
```

Useful for debugging:
- Incorrect turn counts
- Missing tool calls
- Segmentation issues
- Tool linking behavior

## Common Issues

**No evidence extracted**

Check rubric scope versus selector style.

Turn scope requires selectors such as:
- `$.user_query`

Run scope supports selectors such as:
- `$.turns[*].user_query`

**All scores appear neutral**

Evidence extraction may be empty. Inspect:
- `judge_runs.jsonl`

**Unexpected metrics**

Use the adapter inspection tool:
```bash
python -m agent_eval.tools.inspect_adapter_stages trace.json
```

## Optional Integrations

### CloudWatch log export

Exports logs into Generic JSON format compatible with the adapter.

```bash
python -m agent_eval.tools.cloudwatch_extractor \
  --log-group /aws/lambda/my-agent \
  --days 7 \
  --output-dir ./exports
```

Then run evaluation:

```bash
python -m agent_eval.cli \
  --input exports/events.json \
  --judge-config judges.yaml \
  --rubrics rubrics.yaml \
  --output-dir ./output
```

### AgentCore Integration (In Progress)

Future integration will support direct evaluation from AgentCore runtimes:

```
AgentCore runtime
      ↓
CloudWatch OTEL traces
      ↓
NormalizedRun
      ↓
Evaluation artifacts
```

**Current Status:**

| Feature | Status |
|---------|--------|
| Generic JSON Adapter | ✅ Complete |
| Evaluation pipeline | ✅ Complete |
| CloudWatch exporter | ⚠️ Available |
| AgentCore runtime integration | ⚠️ In progress |
| OTEL trace extraction | ⚠️ In progress |

## Testing

The framework includes sample test fixtures for validation. Use the Quick Start command above with the baseline fixtures to verify your setup.

Test fixtures are located in `test-fixtures/` and include:
- Baseline traces (good_001, good_002, good_003)
- Expected results for validation
- Mock judge configurations
- Sample rubric definitions

## Project Structure

```
agent-eval/
  ├── agent_eval/
  │   ├── adapters/          # Trace normalization
  │   ├── evaluators/        # Evaluation pipeline
  │   ├── judges/            # LLM judge clients
  │   ├── schemas/           # JSON schemas
  │   ├── tools/             # Extraction utilities
  │   │   ├── cloudwatch_extractor.py
  │   │   └── agentcore_pipeline/
  │   └── cli.py             # CLI interface
  ├── test-fixtures/         # Sample data and test traces
  └── guides/                # Documentation
```

## Limitations

- Quick start uses mock judges for deterministic pipeline validation
- Real LLM judges require external credentials
- AgentCore integration is still under development
- Some OTEL fields may not be available depending on export method
- Raw traces are expected to contain timestamped events

## Contributing

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Validate installation:

```bash
python -m agent_eval.cli --help
```

## Additional Documentation

- `guides/RUBRIC_SELECTOR_VALIDATION.md`
- `guides/VALIDATION_RESULTS.md`
- `agent_eval/tools/agentcore_pipeline/README.md`
