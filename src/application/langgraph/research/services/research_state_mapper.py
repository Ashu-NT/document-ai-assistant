from __future__ import annotations

from typing import Any

from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.research.models import (
    ResearchEvidence,
    ResearchGap,
    ResearchGapSeverity,
    ResearchGoal,
    ResearchGoalType,
    ResearchOutputType,
    ResearchPlan,
    ResearchReport,
    ResearchResult,
    ResearchSynthesis,
    ResearchTask,
    ResearchTaskResult,
)


class ResearchStateMapper:
    @classmethod
    def plan_from_dict(cls, value: dict[str, Any] | None) -> ResearchPlan | None:
        if not isinstance(value, dict):
            return None
        goal = cls.goal_from_dict(value.get("goal"))
        if goal is None:
            return None
        tasks = cls.tasks_from_list(value.get("tasks"))
        return ResearchPlan(
            plan_id=str(value.get("plan_id") or ""),
            goal=goal,
            tasks=tasks,
            reason=str(value.get("reason") or ""),
            source=str(value.get("source") or ""),
            requires_document=bool(value.get("requires_document", False)),
            max_iterations=int(value.get("max_iterations") or 0),
            diagnostics=dict(value.get("diagnostics") or {}),
        )

    @classmethod
    def result_from_state(cls, state: dict[str, Any]) -> ResearchResult | None:
        plan = cls.plan_from_dict(state.get("research_plan"))
        goal = cls.goal_from_dict(state.get("research_goal"))
        if plan is None or goal is None:
            return None
        return ResearchResult(
            success=bool(state.get("research_result", {}).get("success", True))
            if isinstance(state.get("research_result"), dict)
            else True,
            goal=goal,
            plan=plan,
            task_results=cls.task_results_from_list(state.get("research_task_results")),
            evidence=cls.evidence_from_list(state.get("research_evidence")),
            synthesis=cls.synthesis_from_dict(state.get("research_synthesis")),
            report=cls.report_from_dict(state.get("research_report")),
            gaps=cls.gaps_from_list(state.get("research_gaps")),
            iterations=int(state.get("research_iterations") or 0),
            errors=[str(item) for item in list(state.get("research_errors") or [])],
            diagnostics=dict(state.get("research_result", {}).get("diagnostics") or {})
            if isinstance(state.get("research_result"), dict)
            else {},
        )

    @staticmethod
    def plan_to_state(plan: ResearchPlan) -> dict[str, Any]:
        return {
            "research_goal": serialize_graph_value(plan.goal.to_dict()),
            "research_plan": serialize_graph_value(plan.to_dict()),
        }

    @staticmethod
    def result_to_state(result: ResearchResult) -> dict[str, Any]:
        return {
            "research_goal": serialize_graph_value(result.goal.to_dict()),
            "research_plan": serialize_graph_value(result.plan.to_dict()),
            "research_task_results": serialize_graph_value(
                [task_result.to_dict() for task_result in result.task_results]
            ),
            "research_evidence": serialize_graph_value(
                [evidence.to_dict() for evidence in result.evidence]
            ),
            "research_gaps": serialize_graph_value(
                [gap.to_dict() for gap in result.gaps]
            ),
            "research_iterations": result.iterations,
            "research_synthesis": serialize_graph_value(result.synthesis.to_dict())
            if result.synthesis is not None
            else None,
            "research_report": serialize_graph_value(result.report.to_dict())
            if result.report is not None
            else None,
            "research_errors": list(result.errors),
            "research_result": serialize_graph_value(result.to_dict()),
        }

    @classmethod
    def goal_from_dict(cls, value: Any) -> ResearchGoal | None:
        if not isinstance(value, dict):
            return None
        goal_type = cls._enum_or_none(ResearchGoalType, value.get("goal_type"))
        output_type = cls._enum_or_none(
            ResearchOutputType,
            value.get("expected_output_type"),
        )
        if goal_type is None or output_type is None:
            return None
        return ResearchGoal(
            goal_id=str(value.get("goal_id") or ""),
            user_input=str(value.get("user_input") or ""),
            goal_type=goal_type,
            document_id=cls._str_or_none(value.get("document_id")),
            document_title=cls._str_or_none(value.get("document_title")),
            requires_document=bool(value.get("requires_document", False)),
            requires_cross_section_reasoning=bool(
                value.get("requires_cross_section_reasoning", False)
            ),
            requires_multi_strategy_retrieval=bool(
                value.get("requires_multi_strategy_retrieval", False)
            ),
            expected_output_type=output_type,
            diagnostics=dict(value.get("diagnostics") or {}),
        )

    @classmethod
    def tasks_from_list(cls, value: Any) -> list[ResearchTask]:
        if not isinstance(value, list):
            return []
        tasks: list[ResearchTask] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            tasks.append(
                ResearchTask(
                    task_id=str(item.get("task_id") or ""),
                    title=str(item.get("title") or ""),
                    question=str(item.get("question") or ""),
                    strategy_hint=cls._str_or_none(item.get("strategy_hint")),
                    answer_intent_hint=cls._str_or_none(
                        item.get("answer_intent_hint")
                    ),
                    document_id=cls._str_or_none(item.get("document_id")),
                    required=bool(item.get("required", True)),
                    depends_on=[
                        str(dependency)
                        for dependency in list(item.get("depends_on") or [])
                        if str(dependency).strip()
                    ],
                    expected_evidence_type=cls._str_or_none(
                        item.get("expected_evidence_type")
                    ),
                    max_results=int(item.get("max_results") or 0),
                    diagnostics=dict(item.get("diagnostics") or {}),
                )
            )
        return tasks

    @classmethod
    def task_results_from_list(cls, value: Any) -> list[ResearchTaskResult]:
        if not isinstance(value, list):
            return []
        results: list[ResearchTaskResult] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            results.append(
                ResearchTaskResult(
                    task_id=str(item.get("task_id") or ""),
                    success=bool(item.get("success", False)),
                    tool_names=[
                        str(tool_name)
                        for tool_name in list(item.get("tool_names") or [])
                        if str(tool_name).strip()
                    ],
                    retrieval_strategy=cls._str_or_none(
                        item.get("retrieval_strategy")
                    ),
                    evidence=cls.evidence_from_list(item.get("evidence")),
                    answer_text=cls._str_or_none(item.get("answer_text")),
                    errors=[
                        str(error)
                        for error in list(item.get("errors") or [])
                        if str(error).strip()
                    ],
                    diagnostics=dict(item.get("diagnostics") or {}),
                )
            )
        return results

    @classmethod
    def evidence_from_list(cls, value: Any) -> list[ResearchEvidence]:
        if not isinstance(value, list):
            return []
        evidence: list[ResearchEvidence] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            evidence.append(
                ResearchEvidence(
                    evidence_id=str(item.get("evidence_id") or ""),
                    task_id=str(item.get("task_id") or ""),
                    chunk_id=str(item.get("chunk_id") or ""),
                    document_id=str(item.get("document_id") or ""),
                    document_title=cls._str_or_none(item.get("document_title")),
                    section_path=[
                        str(section)
                        for section in list(item.get("section_path") or [])
                        if str(section).strip()
                    ],
                    page_start=cls._int_or_none(item.get("page_start")),
                    page_end=cls._int_or_none(item.get("page_end")),
                    chunk_type=cls._str_or_none(item.get("chunk_type")),
                    score=cls._float_or_none(item.get("score")),
                    content_excerpt=str(item.get("content_excerpt") or ""),
                    source_tool=str(item.get("source_tool") or ""),
                    diagnostics=dict(item.get("diagnostics") or {}),
                )
            )
        return evidence

    @classmethod
    def gaps_from_list(cls, value: Any) -> list[ResearchGap]:
        if not isinstance(value, list):
            return []
        gaps: list[ResearchGap] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            severity = cls._enum_or_none(ResearchGapSeverity, item.get("severity"))
            if severity is None:
                continue
            gaps.append(
                ResearchGap(
                    gap_id=str(item.get("gap_id") or ""),
                    description=str(item.get("description") or ""),
                    severity=severity,
                    related_task_id=cls._str_or_none(item.get("related_task_id")),
                    suggested_followup_query=cls._str_or_none(
                        item.get("suggested_followup_query")
                    ),
                    suggested_strategy=cls._str_or_none(
                        item.get("suggested_strategy")
                    ),
                    can_retry=bool(item.get("can_retry", False)),
                    diagnostics=dict(item.get("diagnostics") or {}),
                )
            )
        return gaps

    @classmethod
    def synthesis_from_dict(cls, value: Any) -> ResearchSynthesis | None:
        if not isinstance(value, dict):
            return None
        return ResearchSynthesis(
            summary=str(value.get("summary") or ""),
            sections=[
                dict(section)
                for section in list(value.get("sections") or [])
                if isinstance(section, dict)
            ],
            comparisons=[
                dict(comparison)
                for comparison in list(value.get("comparisons") or [])
                if isinstance(comparison, dict)
            ],
            checklist_items=[
                dict(item)
                for item in list(value.get("checklist_items") or [])
                if isinstance(item, dict)
            ],
            gaps=cls.gaps_from_list(value.get("gaps")),
            references=[
                dict(reference)
                for reference in list(value.get("references") or [])
                if isinstance(reference, dict)
            ],
            diagnostics=dict(value.get("diagnostics") or {}),
        )

    @classmethod
    def report_from_dict(cls, value: Any) -> ResearchReport | None:
        if not isinstance(value, dict):
            return None
        return ResearchReport(
            title=str(value.get("title") or ""),
            executive_summary=str(value.get("executive_summary") or ""),
            sections=[
                dict(section)
                for section in list(value.get("sections") or [])
                if isinstance(section, dict)
            ],
            findings=[
                str(item)
                for item in list(value.get("findings") or [])
                if str(item).strip()
            ],
            gaps=[
                dict(gap)
                for gap in list(value.get("gaps") or [])
                if isinstance(gap, dict)
            ],
            references=[
                dict(reference)
                for reference in list(value.get("references") or [])
                if isinstance(reference, dict)
            ],
            appendix=dict(value.get("appendix") or {}),
            diagnostics=dict(value.get("diagnostics") or {}),
        )

    @staticmethod
    def _str_or_none(value: Any) -> str | None:
        if isinstance(value, str) and value:
            return value
        return None

    @staticmethod
    def _int_or_none(value: Any) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _float_or_none(value: Any) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _enum_or_none(enum_type, value: Any):
        if not isinstance(value, str) or not value:
            return None
        try:
            return enum_type(value)
        except ValueError:
            return None
