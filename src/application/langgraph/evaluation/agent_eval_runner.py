from __future__ import annotations

from typing import Any, Callable, Iterable, Sequence
from uuid import uuid4

from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.evaluation.models.agent_eval_result import (
    AgentCaseResult,
    AgentEvalReport,
)
from src.application.langgraph.evaluation.models.agent_test_case import AgentTestCase
from src.application.langgraph.evaluation.execution.agent_eval_turn_runner import (
    run_turn,
)
from src.application.langgraph.evaluation.scoring.agent_eval_case_scorer import (
    evaluate_case,
)
from src.application.langgraph.evaluation.scoring.agent_eval_summary_builder import (
    build_agent_eval_summary,
)
from src.shared.exceptions import SchemaValidationError


class AgentEvalRunner:
    def __init__(
        self,
        *,
        graph: Any | None = None,
        graph_factory: Callable[[], Any] | None = None,
    ) -> None:
        if graph is None and graph_factory is None:
            raise ValueError("AgentEvalRunner requires either graph or graph_factory.")
        self._graph = graph
        self._graph_factory = graph_factory

    def run_cases(
        self,
        cases: Sequence[AgentTestCase],
        *,
        case_ids: Iterable[str] | None = None,
        tags: Iterable[str] | None = None,
        max_cases: int | None = None,
        llm_planning_enabled_override: bool | None = None,
        deep_research_enabled_override: bool | None = None,
        llm_research_planning_enabled_override: bool | None = None,
        answer_generation_enabled_override: bool | None = None,
        retrieval_strategy_enabled_override: bool | None = None,
        llm_retrieval_strategy_enabled_override: bool | None = None,
        requested_retrieval_strategy_override: str | None = None,
        source_path: str | None = None,
    ) -> AgentEvalReport:
        selected_cases = self._select_cases(
            cases,
            case_ids=case_ids,
            tags=tags,
            max_cases=max_cases,
        )
        if not selected_cases:
            raise SchemaValidationError(
                "Agent evaluation selection did not produce any cases.",
                details={
                    "requested_case_ids": sorted(case_ids or []),
                    "requested_tags": sorted(tags or []),
                },
            )

        graph = self._resolve_graph()
        case_results = [
            self._run_case(
                graph,
                case,
                llm_planning_enabled_override=llm_planning_enabled_override,
                deep_research_enabled_override=deep_research_enabled_override,
                llm_research_planning_enabled_override=(
                    llm_research_planning_enabled_override
                ),
                answer_generation_enabled_override=answer_generation_enabled_override,
                retrieval_strategy_enabled_override=retrieval_strategy_enabled_override,
                llm_retrieval_strategy_enabled_override=(
                    llm_retrieval_strategy_enabled_override
                ),
                requested_retrieval_strategy_override=(
                    requested_retrieval_strategy_override
                ),
            )
            for case in selected_cases
        ]
        summary = build_agent_eval_summary(case_results)
        return AgentEvalReport(
            case_results=case_results,
            summary=summary,
            source_path=source_path,
            filters=serialize_graph_value(
                {
                    "case_ids": list(case_ids or []),
                    "tags": list(tags or []),
                    "max_cases": max_cases,
                    "llm_planning_enabled_override": llm_planning_enabled_override,
                    "deep_research_enabled_override": deep_research_enabled_override,
                    "llm_research_planning_enabled_override": (
                        llm_research_planning_enabled_override
                    ),
                    "answer_generation_enabled_override": (
                        answer_generation_enabled_override
                    ),
                    "retrieval_strategy_enabled_override": (
                        retrieval_strategy_enabled_override
                    ),
                    "llm_retrieval_strategy_enabled_override": (
                        llm_retrieval_strategy_enabled_override
                    ),
                    "requested_retrieval_strategy_override": (
                        requested_retrieval_strategy_override
                    ),
                }
            ),
        )

    def _resolve_graph(self) -> Any:
        if self._graph is not None:
            return self._graph
        assert self._graph_factory is not None
        self._graph = self._graph_factory()
        return self._graph

    def _select_cases(
        self,
        cases: Sequence[AgentTestCase],
        *,
        case_ids: Iterable[str] | None,
        tags: Iterable[str] | None,
        max_cases: int | None,
    ) -> list[AgentTestCase]:
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

    def _run_case(
        self,
        graph: Any,
        case: AgentTestCase,
        *,
        llm_planning_enabled_override: bool | None,
        deep_research_enabled_override: bool | None,
        llm_research_planning_enabled_override: bool | None,
        answer_generation_enabled_override: bool | None,
        retrieval_strategy_enabled_override: bool | None,
        llm_retrieval_strategy_enabled_override: bool | None,
        requested_retrieval_strategy_override: str | None,
    ) -> AgentCaseResult:
        session_id = f"agent-eval-{case.case_id.lower()}-{uuid4().hex[:8]}"
        turn_results = [
            run_turn(
                graph,
                turn_input,
                session_id=session_id,
                llm_planning_enabled_override=llm_planning_enabled_override,
                deep_research_enabled_override=deep_research_enabled_override,
                llm_research_planning_enabled_override=(
                    llm_research_planning_enabled_override
                ),
                answer_generation_enabled_override=answer_generation_enabled_override,
                retrieval_strategy_enabled_override=retrieval_strategy_enabled_override,
                llm_retrieval_strategy_enabled_override=(
                    llm_retrieval_strategy_enabled_override
                ),
                requested_retrieval_strategy_override=(
                    requested_retrieval_strategy_override
                ),
            )
            for turn_input in case.inputs
        ]
        failed_checks, metrics, diagnostics = evaluate_case(
            case.expected,
            turn_results=turn_results,
        )
        return AgentCaseResult(
            case_id=case.case_id,
            name=case.name,
            passed=not failed_checks,
            failed_checks=failed_checks,
            turn_results=turn_results,
            metrics=metrics,
            diagnostics=serialize_graph_value(
                {
                    "expected": case.expected,
                    "session_id": session_id,
                    **diagnostics,
                }
            ),
        )
