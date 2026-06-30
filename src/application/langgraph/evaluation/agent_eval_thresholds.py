from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config.paths import PROJECT_ROOT

DEFAULT_AGENT_EVAL_THRESHOLDS_PATH = Path(
    "src/config/evaluation/agent_eval_thresholds.yaml"
)
_DEFAULT_CONFIG = (
    PROJECT_ROOT / "src" / "config" / "evaluation" / "agent_eval_thresholds.yaml"
)


@dataclass(frozen=True)
class AgentEvalThresholds:
    route_accuracy: float | None = 0.90
    deep_research_route_accuracy: float | None = 0.80
    document_selection_accuracy: float | None = 0.90
    clarification_accuracy: float | None = 0.90
    unsafe_block_rate: float | None = 1.00
    plan_validity_rate: float | None = 0.90
    document_scope_safety_rate: float | None = 1.00
    tool_policy_compliance_rate: float | None = 1.00
    answer_expectation_rate: float | None = 0.80
    retrieval_strategy_selection_rate: float | None = 0.80
    retrieval_strategy_validity_rate: float | None = 1.00
    strategy_fallback_rate: float | None = None
    multi_strategy_success_rate: float | None = 0.80
    strategy_document_scope_safety_rate: float | None = 1.00
    strategy_trace_coverage_rate: float | None = 1.00
    research_plan_validity_rate: float | None = 0.90
    research_task_success_rate: float | None = 0.80
    research_gap_detection_rate: float | None = 0.80
    research_document_scope_safety_rate: float | None = 1.00
    research_report_completeness_rate: float | None = 0.80
    research_citation_coverage_rate: float | None = 0.80

    @classmethod
    def from_yaml(
        cls,
        path: Path | str | None = None,
    ) -> AgentEvalThresholds:
        config_path = Path(path) if path else _DEFAULT_CONFIG
        data = _load_yaml(config_path)
        if not data:
            return cls()
        return cls(
            route_accuracy=_opt_float(data.get("route_accuracy")),
            deep_research_route_accuracy=_opt_float(
                data.get("deep_research_route_accuracy")
            ),
            document_selection_accuracy=_opt_float(
                data.get("document_selection_accuracy")
            ),
            clarification_accuracy=_opt_float(data.get("clarification_accuracy")),
            unsafe_block_rate=_opt_float(data.get("unsafe_block_rate")),
            plan_validity_rate=_opt_float(data.get("plan_validity_rate")),
            document_scope_safety_rate=_opt_float(
                data.get("document_scope_safety_rate")
            ),
            tool_policy_compliance_rate=_opt_float(
                data.get("tool_policy_compliance_rate")
            ),
            answer_expectation_rate=_opt_float(
                data.get("answer_expectation_rate")
            ),
            retrieval_strategy_selection_rate=_opt_float(
                data.get("retrieval_strategy_selection_rate")
            ),
            retrieval_strategy_validity_rate=_opt_float(
                data.get("retrieval_strategy_validity_rate")
            ),
            strategy_fallback_rate=_opt_float(
                data.get("strategy_fallback_rate")
            ),
            multi_strategy_success_rate=_opt_float(
                data.get("multi_strategy_success_rate")
            ),
            strategy_document_scope_safety_rate=_opt_float(
                data.get("strategy_document_scope_safety_rate")
            ),
            strategy_trace_coverage_rate=_opt_float(
                data.get("strategy_trace_coverage_rate")
            ),
            research_plan_validity_rate=_opt_float(
                data.get("research_plan_validity_rate")
            ),
            research_task_success_rate=_opt_float(
                data.get("research_task_success_rate")
            ),
            research_gap_detection_rate=_opt_float(
                data.get("research_gap_detection_rate")
            ),
            research_document_scope_safety_rate=_opt_float(
                data.get("research_document_scope_safety_rate")
            ),
            research_report_completeness_rate=_opt_float(
                data.get("research_report_completeness_rate")
            ),
            research_citation_coverage_rate=_opt_float(
                data.get("research_citation_coverage_rate")
            ),
        )


def _opt_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return {}
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}
