from __future__ import annotations

"""
Run LangGraph agent evaluation against the real document agent graph.

Usage:
    python scripts/run_agent_eval.py
    python scripts/run_agent_eval.py --tag safety --llm-planning --fail-on-threshold
    python scripts/run_agent_eval.py --case-id AG-010 --json
"""

import argparse
import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
SCRIPT_ROOT = Path(__file__).resolve().parent

for import_root in (PROJECT_ROOT, SRC_ROOT, SCRIPT_ROOT):
    import_root_text = str(import_root)
    if import_root_text not in sys.path:
        sys.path.insert(0, import_root_text)

import agent_cli  # noqa: E402

from src.application.langgraph.evaluation import (  # noqa: E402
    AgentEvalLoader,
    AgentEvalReportWriter,
    AgentEvalRunner,
    AgentQualityGate,
    DEFAULT_AGENT_EVAL_CASES_PATH,
    DEFAULT_AGENT_EVAL_THRESHOLDS_PATH,
)
from src.config.paths import resolve_project_path  # noqa: E402
from src.shared.exceptions import ApplicationError, SchemaValidationError  # noqa: E402

_QUALITY_GATE_FAILURE_EXIT_CODE = 2


@dataclass(slots=True)
class AgentEvalRuntime:
    graph_runtime: Any
    runner: AgentEvalRunner
    loader: AgentEvalLoader
    report_writer: AgentEvalReportWriter
    quality_gate: AgentQualityGate


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the LangGraph agent evaluation suite."
    )
    parser.add_argument(
        "--cases",
        default=str(DEFAULT_AGENT_EVAL_CASES_PATH),
        help="Optional agent evaluation YAML or JSON case file.",
    )
    parser.add_argument(
        "--thresholds",
        default=str(DEFAULT_AGENT_EVAL_THRESHOLDS_PATH),
        help="Optional agent evaluation thresholds YAML path.",
    )
    parser.add_argument(
        "--case-id",
        action="append",
        default=[],
        help="Restrict evaluation to one or more specific case IDs.",
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Restrict evaluation to one or more tags.",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=None,
        help="Optional maximum number of filtered cases to run.",
    )
    llm_planning_group = parser.add_mutually_exclusive_group()
    llm_planning_group.add_argument(
        "--llm-planning",
        dest="llm_planning",
        action="store_true",
        help="Force LLM planning on for all evaluated turns.",
    )
    llm_planning_group.add_argument(
        "--no-llm-planning",
        dest="llm_planning",
        action="store_false",
        help="Force LLM planning off for all evaluated turns.",
    )
    parser.set_defaults(llm_planning=None)
    deep_research_group = parser.add_mutually_exclusive_group()
    deep_research_group.add_argument(
        "--deep-research",
        dest="deep_research",
        action="store_true",
        help="Force deep research on for all evaluated turns.",
    )
    deep_research_group.add_argument(
        "--no-deep-research",
        dest="deep_research",
        action="store_false",
        help="Force deep research off for all evaluated turns.",
    )
    parser.set_defaults(deep_research=None)
    llm_research_planning_group = parser.add_mutually_exclusive_group()
    llm_research_planning_group.add_argument(
        "--llm-research-planning",
        dest="llm_research_planning",
        action="store_true",
        help="Force validated LLM research planning on for all evaluated turns.",
    )
    llm_research_planning_group.add_argument(
        "--no-llm-research-planning",
        dest="llm_research_planning",
        action="store_false",
        help="Force validated LLM research planning off for all evaluated turns.",
    )
    parser.set_defaults(llm_research_planning=None)
    parser.add_argument(
        "--retrieval-strategy",
        choices=(
            "auto",
            "hybrid",
            "identifier",
            "table",
            "section",
            "figure",
            "maintenance",
            "procedure",
            "specification",
            "troubleshooting",
            "certification",
            "drawing",
        ),
        default=None,
        help="Optional retrieval strategy override for all evaluated turns.",
    )
    llm_retrieval_strategy_group = parser.add_mutually_exclusive_group()
    llm_retrieval_strategy_group.add_argument(
        "--llm-retrieval-strategy",
        dest="llm_retrieval_strategy",
        action="store_true",
        help="Force validated LLM retrieval-strategy selection on for all turns.",
    )
    llm_retrieval_strategy_group.add_argument(
        "--no-llm-retrieval-strategy",
        dest="llm_retrieval_strategy",
        action="store_false",
        help="Force validated LLM retrieval-strategy selection off for all turns.",
    )
    parser.set_defaults(llm_retrieval_strategy=None)
    generation_group = parser.add_mutually_exclusive_group()
    generation_group.add_argument(
        "--generate",
        dest="generate",
        action="store_true",
        help="Force answer generation on for all evaluated turns.",
    )
    generation_group.add_argument(
        "--no-generate",
        dest="generate",
        action="store_false",
        help="Force answer generation off for all evaluated turns.",
    )
    parser.set_defaults(generate=None)
    parser.add_argument(
        "--output-dir",
        help="Optional output directory. Defaults to outputs/evaluation/agent",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the serialized report to stdout after writing files.",
    )
    parser.add_argument(
        "--fail-on-threshold",
        action="store_true",
        help="Exit non-zero when the agent quality gate fails.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[agent-eval] {message}", flush=True)


def resolve_path(value: str | None) -> Path | None:
    if value is None:
        return None
    return resolve_project_path(value).expanduser().resolve()


def default_output_directory() -> Path:
    from src.config.settings import storage_settings  # noqa: WPS433

    return (storage_settings.evaluation_output_path / "agent").resolve()


def build_runtime(
    *,
    enable_generation: bool,
    enable_llm_planning: bool,
    enable_deep_research: bool,
    enable_llm_research_planning: bool,
    thresholds_path: Path | None,
) -> AgentEvalRuntime:
    from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
    from src.infrastructure.db.base import Base  # noqa: WPS433
    from src.infrastructure.db.schema_management import ensure_database_schema  # noqa: WPS433
    from src.infrastructure.db.orm_models import (  # noqa: WPS433,F401
        __all__ as _orm_models_loaded,
    )
    from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433

    bootstrap_application()
    ensure_database_schema(engine)
    session = SessionLocal()
    _ = enable_deep_research
    graph_runtime = agent_cli.build_agent_runtime(
        session,
        enable_generation=enable_generation,
        enable_llm_planning=enable_llm_planning,
        enable_llm_research_planning=enable_llm_research_planning,
    )
    return AgentEvalRuntime(
        graph_runtime=graph_runtime,
        runner=AgentEvalRunner(graph=graph_runtime.graph),
        loader=AgentEvalLoader(),
        report_writer=AgentEvalReportWriter(),
        quality_gate=AgentQualityGate(thresholds_path=thresholds_path),
    )


def resolve_output_paths(output_directory: Path) -> tuple[Path, Path]:
    return (
        (output_directory / "agent_eval_report.json").resolve(),
        (output_directory / "agent_eval_report.md").resolve(),
    )


def select_cases(
    cases,
    *,
    case_ids: Iterable[str] | None,
    tags: Iterable[str] | None,
    max_cases: int | None,
):
    requested_ids = {case_id for case_id in (case_ids or []) if case_id}
    requested_tags = {tag for tag in (tags or []) if tag}
    selected = [
        case
        for case in cases
        if (not requested_ids or case.case_id in requested_ids)
        and (not requested_tags or requested_tags.intersection(case.tags))
    ]
    if max_cases is not None and max_cases >= 0:
        selected = selected[:max_cases]
    return selected


def needs_llm_planning(cases, override: bool | None) -> bool:
    if override is False:
        return False
    if override is True:
        return True
    return any(
        turn.llm_planning_enabled
        for case in cases
        for turn in case.inputs
    )


def needs_deep_research(cases, override: bool | None) -> bool:
    if override is False:
        return False
    if override is True:
        return True
    return any(
        turn.deep_research_enabled
        for case in cases
        for turn in case.inputs
    )


def needs_llm_research_planning(cases, override: bool | None) -> bool:
    if override is False:
        return False
    if override is True:
        return True
    return any(
        turn.llm_research_planning_enabled
        for case in cases
        for turn in case.inputs
    )


def needs_generation(cases, override: bool | None) -> bool:
    if override is False:
        return False
    if override is True:
        return True
    return any(
        turn.allow_answer_generation
        for case in cases
        for turn in case.inputs
    )


def run_agent_eval(
    *,
    cases_path: Path,
    thresholds_path: Path | None,
    case_ids: list[str],
    tags: list[str],
    max_cases: int | None,
    llm_planning_override: bool | None,
    deep_research_override: bool | None,
    llm_research_planning_override: bool | None,
    generation_override: bool | None,
    retrieval_strategy_override: str | None,
    llm_retrieval_strategy_override: bool | None,
    output_directory: Path,
) -> tuple[Any, Any]:
    loader = AgentEvalLoader()
    all_cases = loader.load(cases_path)
    selected_cases = select_cases(
        all_cases,
        case_ids=case_ids,
        tags=tags,
        max_cases=max_cases,
    )
    if not selected_cases:
        raise SchemaValidationError(
            "Agent evaluation selection did not produce any cases.",
            details={
                "cases_path": str(cases_path),
                "requested_case_ids": case_ids,
                "requested_tags": tags,
            },
        )

    print_status(f"Loaded {len(all_cases)} case(s) from {cases_path}")
    print_status(f"Selected {len(selected_cases)} case(s) for evaluation.")
    enable_llm_planning = needs_llm_planning(selected_cases, llm_planning_override)
    enable_deep_research = needs_deep_research(
        selected_cases,
        deep_research_override,
    )
    enable_llm_research_planning = needs_llm_research_planning(
        selected_cases,
        llm_research_planning_override,
    )
    enable_generation = needs_generation(selected_cases, generation_override)
    print_status(
        "Runtime flags: "
        f"llm_planning={enable_llm_planning}, "
        f"deep_research={enable_deep_research}, "
        f"llm_research_planning={enable_llm_research_planning}, "
        f"answer_generation={enable_generation}"
    )
    print_status("Building agent evaluation runtime...")
    runtime = build_runtime(
        enable_generation=enable_generation,
        enable_llm_planning=enable_llm_planning,
        enable_deep_research=enable_deep_research,
        enable_llm_research_planning=enable_llm_research_planning,
        thresholds_path=thresholds_path,
    )
    print_status("Agent evaluation runtime ready.")
    try:
        print_status("Running agent evaluation cases...")
        report = runtime.runner.run_cases(
            all_cases,
            case_ids=case_ids,
            tags=tags,
            max_cases=max_cases,
            llm_planning_enabled_override=llm_planning_override,
            deep_research_enabled_override=deep_research_override,
            llm_research_planning_enabled_override=(
                llm_research_planning_override
            ),
            answer_generation_enabled_override=generation_override,
            retrieval_strategy_enabled_override=(
                True
                if retrieval_strategy_override is not None
                or llm_retrieval_strategy_override is True
                else None
            ),
            llm_retrieval_strategy_enabled_override=(
                llm_retrieval_strategy_override
            ),
            requested_retrieval_strategy_override=retrieval_strategy_override,
            source_path=str(cases_path),
        )
        print_status("Evaluating agent quality gate...")
        gate_result = runtime.quality_gate.check(report)
        json_output_path, markdown_output_path = resolve_output_paths(output_directory)
        print_status(f"Writing JSON report to {json_output_path}...")
        runtime.report_writer.write_json(
            report,
            json_output_path,
            quality_gate_result=gate_result,
        )
        print_status(f"Writing Markdown report to {markdown_output_path}...")
        runtime.report_writer.write_markdown(
            report,
            markdown_output_path,
            quality_gate_result=gate_result,
        )
        return runtime, (report, gate_result, json_output_path, markdown_output_path)
    except Exception:
        agent_cli.close_runtime(runtime.graph_runtime)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    cases_path = resolve_path(args.cases)
    thresholds_path = resolve_path(args.thresholds)
    output_directory = resolve_path(args.output_dir) or default_output_directory()
    runtime = None

    try:
        print_status(f"Cases path: {cases_path}")
        print_status(f"Thresholds path: {thresholds_path}")
        print_status(f"Output directory: {output_directory}")
        runtime, result = run_agent_eval(
            cases_path=cases_path,
            thresholds_path=thresholds_path,
            case_ids=args.case_id,
            tags=args.tag,
            max_cases=args.max_cases,
            llm_planning_override=args.llm_planning,
            deep_research_override=args.deep_research,
            llm_research_planning_override=args.llm_research_planning,
            generation_override=args.generate,
            retrieval_strategy_override=args.retrieval_strategy,
            llm_retrieval_strategy_override=args.llm_retrieval_strategy,
            output_directory=output_directory,
        )
        report, gate_result, json_output_path, markdown_output_path = result
        summary = report.summary
        print(f"case_count: {summary.case_count}")
        print(f"passed_count: {summary.passed_count}")
        print(f"failed_count: {summary.failed_count}")
        print(f"route_accuracy: {summary.route_accuracy:.3f}")
        print(f"document_selection_accuracy: {summary.document_selection_accuracy:.3f}")
        print(f"clarification_accuracy: {summary.clarification_accuracy:.3f}")
        print(f"unsafe_block_rate: {summary.unsafe_block_rate:.3f}")
        print(f"plan_validity_rate: {summary.plan_validity_rate:.3f}")
        print(f"document_scope_safety_rate: {summary.document_scope_safety_rate:.3f}")
        print(
            f"tool_policy_compliance_rate: {summary.tool_policy_compliance_rate:.3f}"
        )
        print(f"answer_expectation_rate: {summary.answer_expectation_rate:.3f}")
        print(
            "retrieval_strategy_selection_rate: "
            f"{summary.retrieval_strategy_selection_rate:.3f}"
        )
        print(
            "retrieval_strategy_validity_rate: "
            f"{summary.retrieval_strategy_validity_rate:.3f}"
        )
        print(f"strategy_fallback_rate: {summary.strategy_fallback_rate:.3f}")
        print(
            "multi_strategy_success_rate: "
            f"{summary.multi_strategy_success_rate:.3f}"
        )
        print(
            "strategy_document_scope_safety_rate: "
            f"{summary.strategy_document_scope_safety_rate:.3f}"
        )
        print(
            "strategy_trace_coverage_rate: "
            f"{summary.strategy_trace_coverage_rate:.3f}"
        )
        print(
            "deep_research_route_accuracy: "
            f"{summary.deep_research_route_accuracy:.3f}"
        )
        print(
            "research_plan_validity_rate: "
            f"{summary.research_plan_validity_rate:.3f}"
        )
        print(
            "research_task_success_rate: "
            f"{summary.research_task_success_rate:.3f}"
        )
        print(
            "research_gap_detection_rate: "
            f"{summary.research_gap_detection_rate:.3f}"
        )
        print(
            "research_document_scope_safety_rate: "
            f"{summary.research_document_scope_safety_rate:.3f}"
        )
        print(
            "research_report_completeness_rate: "
            f"{summary.research_report_completeness_rate:.3f}"
        )
        print(
            "research_citation_coverage_rate: "
            f"{summary.research_citation_coverage_rate:.3f}"
        )
        print(f"threshold_passed: {gate_result.passed}")
        print(json_output_path)
        print(markdown_output_path)

        if args.json:
            print(
                json.dumps(
                    runtime.report_writer.serialize(
                        report,
                        quality_gate_result=gate_result,
                    ),
                    indent=2,
                )
            )

        if args.fail_on_threshold and not gate_result.passed:
            return _QUALITY_GATE_FAILURE_EXIT_CODE
        return 0
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except SchemaValidationError as exc:
        print(f"{exc.error_code}: {exc.message}", file=sys.stderr)
        if exc.details:
            print(json.dumps(exc.details, indent=2), file=sys.stderr)
        return 1
    except ApplicationError as exc:
        print(f"{exc.error_code}: {exc.message}", file=sys.stderr)
        if exc.details:
            print(json.dumps(exc.details, indent=2), file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if runtime is not None:
            agent_cli.close_runtime(runtime.graph_runtime)


if __name__ == "__main__":
    raise SystemExit(main())
