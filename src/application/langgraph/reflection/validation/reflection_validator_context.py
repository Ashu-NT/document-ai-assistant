from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.application.langgraph.reflection.detectors.identifier_inventory_context_detector import (
    is_selected_document_identifier_inventory_context,
)
from src.application.langgraph.reflection.detectors.maintenance_interval_context_detector import (
    is_selected_document_maintenance_interval_context,
)
from src.application.langgraph.reflection.detectors.spare_parts_list_context_detector import (
    is_selected_document_spare_parts_list_context,
)
from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
    SufficiencyVerdict,
)


@dataclass(slots=True, frozen=True)
class ValidatorDowngradeContext:
    """Bundles the downgrade-leniency signals every extracted `validate()`
    check consults -- avoids re-threading the same handful of keyword args
    through every check function."""

    diagnostics: dict[str, Any]
    hard_grounding_violation: Any
    maintenance_interval_context: bool
    identifier_inventory_context: bool
    spare_parts_list_context: bool
    generic_context_applies: bool
    downgrade_evidence_description: str


def build_downgrade_context(
    *,
    decision: ReflectionDecision,
    question: str,
    answer_intent: str | None,
    selected_document_id: str | None,
    has_useful_evidence: bool,
    has_relevant_maintenance_evidence: bool,
    has_relevant_spare_parts_evidence: bool,
    generic_sufficiency_verdict: SufficiencyVerdict | None,
) -> ValidatorDowngradeContext:
    maintenance_interval_context = is_selected_document_maintenance_interval_context(
        question=question,
        answer_intent=answer_intent,
        selected_document_id=selected_document_id,
        has_relevant_maintenance_evidence=has_relevant_maintenance_evidence,
    )
    identifier_inventory_context = is_selected_document_identifier_inventory_context(
        question=question,
        answer_intent=answer_intent,
        selected_document_id=selected_document_id,
        has_useful_evidence=has_useful_evidence,
    )
    spare_parts_list_context = is_selected_document_spare_parts_list_context(
        question=question,
        has_relevant_spare_parts_evidence=has_relevant_spare_parts_evidence,
    )
    # Additive, intent-agnostic fallback for the pure-context downgrade gates
    # (none of which have their own domain content check -- unlike the
    # spare-parts/identifier checks, which already inspect answer_text and
    # are left untouched). Only ever true when NONE of the 3 keyword-driven
    # domain contexts matched, so it can only ever add new leniency for
    # questions those 3 don't cover -- it can never change behavior for an
    # already-matched domain context, and is `None`/inert for any caller
    # that doesn't pass it (every existing test).
    generic_context_applies = (
        generic_sufficiency_verdict is not None
        and generic_sufficiency_verdict.is_sufficient
        and not maintenance_interval_context
        and not identifier_inventory_context
        and not spare_parts_list_context
    )
    return ValidatorDowngradeContext(
        diagnostics=dict(decision.diagnostics),
        hard_grounding_violation=decision.diagnostics.get("hard_grounding_violation"),
        maintenance_interval_context=maintenance_interval_context,
        identifier_inventory_context=identifier_inventory_context,
        spare_parts_list_context=spare_parts_list_context,
        generic_context_applies=generic_context_applies,
        downgrade_evidence_description=(
            "maintenance interval evidence" if maintenance_interval_context else "evidence"
        ),
    )


def accept_with_limitations(
    *,
    confidence: float,
    reason: str,
    diagnostics: dict[str, Any],
) -> ReflectionDecision:
    return ReflectionDecision(
        decision=ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
        confidence=confidence,
        reason=reason,
        diagnostics=diagnostics,
    )
