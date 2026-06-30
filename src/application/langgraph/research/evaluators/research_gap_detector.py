from __future__ import annotations

import re

from src.application.langgraph.research.models import (
    ResearchGap,
    ResearchGapSeverity,
)
from src.application.langgraph.research.models.research_goal import ResearchGoalType
from src.shared.ids import IdGenerator


class ResearchGapDetector:
    def __init__(self, *, id_generator: IdGenerator | None = None) -> None:
        self.id_generator = id_generator or IdGenerator()

    def detect(self, result, *, coverage: dict) -> list[ResearchGap]:
        gaps: list[ResearchGap] = []
        task_result_map = {task_result.task_id: task_result for task_result in result.task_results}

        for task in result.plan.tasks:
            task_result = task_result_map.get(task.task_id)
            if task.required and (task_result is None or not task_result.evidence):
                gaps.append(
                    ResearchGap(
                        gap_id=self.id_generator.new_id("research_gap"),
                        description=f"Required task '{task.title}' did not return evidence.",
                        severity=ResearchGapSeverity.HIGH,
                        related_task_id=task.task_id,
                        suggested_followup_query=task.question,
                        suggested_strategy=task.strategy_hint,
                        can_retry=True,
                    )
                )

        if (
            result.goal.goal_type == ResearchGoalType.COMPARISON
            and sum(1 for task_result in result.task_results if task_result.evidence) < 2
        ):
            gaps.append(
                ResearchGap(
                    gap_id=self.id_generator.new_id("research_gap"),
                    description="Comparison evidence is one-sided.",
                    severity=ResearchGapSeverity.HIGH,
                    related_task_id=None,
                    suggested_followup_query=result.goal.user_input,
                    suggested_strategy=None,
                    can_retry=True,
                )
            )

        if result.goal.requires_cross_section_reasoning and coverage.get("section_count", 0) <= 1:
            gaps.append(
                ResearchGap(
                    gap_id=self.id_generator.new_id("research_gap"),
                    description="Evidence came from too few sections for cross-section reasoning.",
                    severity=ResearchGapSeverity.MEDIUM,
                    related_task_id=None,
                    suggested_followup_query=result.goal.user_input,
                    suggested_strategy=None,
                    can_retry=True,
                )
            )

        if result.goal.goal_type == ResearchGoalType.CHECKLIST:
            safety_hits = sum(
                1
                for task in result.plan.tasks
                if "safety" in task.title.lower()
                and task_result_map.get(task.task_id) is not None
                and task_result_map[task.task_id].evidence
            )
            if safety_hits == 0:
                gaps.append(
                    ResearchGap(
                        gap_id=self.id_generator.new_id("research_gap"),
                        description="Checklist evidence is missing safety support.",
                        severity=ResearchGapSeverity.MEDIUM,
                        related_task_id=None,
                        suggested_followup_query="What safety warnings apply to this checklist request?",
                        suggested_strategy=None,
                        can_retry=True,
                    )
                )

        if result.goal.goal_type == ResearchGoalType.GAP_ANALYSIS:
            focus_terms = _extract_focus_terms(result.goal.user_input)
            uncovered_terms = _uncovered_focus_terms(result.evidence, focus_terms)
            max_focus_terms_in_single_evidence = _max_focus_terms_in_single_evidence(
                result.evidence,
                focus_terms,
            )
            if uncovered_terms:
                gaps.append(
                    ResearchGap(
                        gap_id=self.id_generator.new_id("research_gap"),
                        description=(
                            "The available evidence does not directly cover the requested "
                            f"focus terms: {', '.join(uncovered_terms)}."
                        ),
                        severity=ResearchGapSeverity.HIGH,
                        related_task_id=None,
                        suggested_followup_query=result.goal.user_input,
                        suggested_strategy=None,
                        can_retry=True,
                        diagnostics={"uncovered_focus_terms": uncovered_terms},
                    )
                )
            elif (
                len(focus_terms) >= 2
                and max_focus_terms_in_single_evidence < min(2, len(focus_terms))
            ):
                gaps.append(
                    ResearchGap(
                        gap_id=self.id_generator.new_id("research_gap"),
                        description=(
                            "The available evidence does not cover the requested focus "
                            "terms together in a direct evidence chunk."
                        ),
                        severity=ResearchGapSeverity.HIGH,
                        related_task_id=None,
                        suggested_followup_query=result.goal.user_input,
                        suggested_strategy=None,
                        can_retry=True,
                        diagnostics={
                            "focus_terms": focus_terms,
                            "max_focus_terms_in_single_evidence": (
                                max_focus_terms_in_single_evidence
                            ),
                        },
                    )
                )
            else:
                gap_probe_evidence = _gap_probe_evidence(
                    result.plan.tasks,
                    task_result_map,
                )
                if gap_probe_evidence:
                    probe_max_focus_terms = _max_focus_terms_in_single_evidence(
                        gap_probe_evidence,
                        focus_terms,
                    )
                    if probe_max_focus_terms < len(focus_terms):
                        gaps.append(
                            ResearchGap(
                                gap_id=self.id_generator.new_id("research_gap"),
                                description=(
                                    "Related sections were found, but they do not provide "
                                    "complete direct evidence for the requested claim."
                                ),
                                severity=ResearchGapSeverity.MEDIUM,
                                related_task_id=None,
                                suggested_followup_query=result.goal.user_input,
                                suggested_strategy=None,
                                can_retry=True,
                                diagnostics={
                                    "focus_terms": focus_terms,
                                    "gap_probe_evidence_count": len(gap_probe_evidence),
                                    "gap_probe_max_focus_terms": probe_max_focus_terms,
                                },
                            )
                        )

        return gaps


_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_GAP_STOP_WORDS = {
    "a",
    "all",
    "an",
    "and",
    "are",
    "direct",
    "evidence",
    "find",
    "for",
    "identify",
    "in",
    "is",
    "missing",
    "of",
    "or",
    "related",
    "request",
    "sections",
    "show",
    "that",
    "the",
    "this",
    "what",
}


def _extract_focus_terms(user_input: str) -> list[str]:
    ordered: list[str] = []
    for token in _TOKEN_PATTERN.findall(user_input.lower()):
        if token in _GAP_STOP_WORDS:
            continue
        if len(token) <= 2:
            continue
        if token not in ordered:
            ordered.append(token)
    return ordered


def _uncovered_focus_terms(evidence_items, focus_terms: list[str]) -> list[str]:
    if not focus_terms:
        return []
    covered_terms: set[str] = set()
    for item in evidence_items:
        haystack = " ".join(
            [
                getattr(item, "content_excerpt", "") or "",
                " ".join(getattr(item, "section_path", []) or []),
            ]
        ).lower()
        for term in focus_terms:
            if term in haystack:
                covered_terms.add(term)
    return [term for term in focus_terms if term not in covered_terms]


def _max_focus_terms_in_single_evidence(evidence_items, focus_terms: list[str]) -> int:
    if not focus_terms:
        return 0
    max_matches = 0
    for item in evidence_items:
        haystack = " ".join(
            [
                getattr(item, "content_excerpt", "") or "",
                " ".join(getattr(item, "section_path", []) or []),
            ]
        ).lower()
        matched_terms = {term for term in focus_terms if term in haystack}
        if len(matched_terms) > max_matches:
            max_matches = len(matched_terms)
    return max_matches


def _gap_probe_evidence(plan_tasks, task_result_map: dict[str, object]) -> list[object]:
    evidence_items: list[object] = []
    for task in plan_tasks:
        if getattr(task, "expected_evidence_type", None) != "gap_probe":
            continue
        task_result = task_result_map.get(task.task_id)
        if task_result is None:
            continue
        evidence_items.extend(list(getattr(task_result, "evidence", []) or []))
    return evidence_items
