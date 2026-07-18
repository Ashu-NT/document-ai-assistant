from tests.unit.application.langgraph.reflection.strategies.evidence_sufficiency._evidence_sufficiency_test_helpers import (
    make_context,
)

from src.application.langgraph.reflection.models import SufficiencyVerdict, SufficiencyVerdictType
from src.application.langgraph.reflection.strategies.evidence_sufficiency import (
    EvidenceSufficiencyStrategyRegistry,
    GenericEvidenceSufficiencyStrategy,
    IdentifierInventoryEvidenceSufficiencyStrategy,
    MaintenanceIntervalEvidenceSufficiencyStrategy,
    SparePartsListEvidenceSufficiencyStrategy,
)


def test_registry_dispatches_maintenance_intent_to_the_maintenance_strategy() -> None:
    registry = EvidenceSufficiencyStrategyRegistry()

    assert isinstance(
        registry.for_intent("maintenance"), MaintenanceIntervalEvidenceSufficiencyStrategy
    )


def test_registry_dispatches_table_intent_to_the_spare_parts_strategy() -> None:
    registry = EvidenceSufficiencyStrategyRegistry()

    assert isinstance(
        registry.for_intent("table"), SparePartsListEvidenceSufficiencyStrategy
    )


def test_registry_dispatches_identifier_intent_to_the_identifier_strategy() -> None:
    registry = EvidenceSufficiencyStrategyRegistry()

    assert isinstance(
        registry.for_intent("identifier"), IdentifierInventoryEvidenceSufficiencyStrategy
    )


def test_registry_falls_back_to_generic_for_an_unregistered_intent() -> None:
    registry = EvidenceSufficiencyStrategyRegistry()

    for intent in (
        "troubleshooting",
        "safety",
        "procedure",
        "specification",
        "overview",
        "figure",
        "general",
        "document_exploration",
        None,
        "",
        "an_intent_nobody_registered_yet",
    ):
        assert isinstance(registry.for_intent(intent), GenericEvidenceSufficiencyStrategy)


def test_registry_dispatch_is_case_insensitive() -> None:
    registry = EvidenceSufficiencyStrategyRegistry()

    assert isinstance(
        registry.for_intent("MAINTENANCE"), MaintenanceIntervalEvidenceSufficiencyStrategy
    )


def test_registry_evaluate_returns_a_real_verdict_for_the_dispatched_strategy() -> None:
    registry = EvidenceSufficiencyStrategyRegistry()
    context = make_context(
        question="What are the maintenance intervals?",
        answer_intent="maintenance_summary",
        answer_text="Weekly maintenance latest after 100 operating hours.",
        approved_chunks=[
            {
                "document_id": "doc_1",
                "chunk_type": "maintenance_interval",
                "content": "Perform weekly maintenance every 100 operating hours.",
            }
        ],
    )

    verdict = registry.evaluate(retrieval_query_intent="maintenance", context=context)

    assert verdict.verdict == SufficiencyVerdictType.SUFFICIENT


def test_registry_accepts_custom_strategies_and_default() -> None:
    class _AlwaysInsufficient:
        def is_answer_sufficient(self, context):
            return SufficiencyVerdict(
                verdict=SufficiencyVerdictType.INSUFFICIENT_CLARIFY,
                reason="custom",
            )

    registry = EvidenceSufficiencyStrategyRegistry(
        strategies_by_intent={"safety": _AlwaysInsufficient()},
        default_strategy=_AlwaysInsufficient(),
    )

    verdict = registry.evaluate(
        retrieval_query_intent="safety", context=make_context()
    )

    assert verdict.verdict == SufficiencyVerdictType.INSUFFICIENT_CLARIFY
    assert isinstance(registry.for_intent("procedure"), _AlwaysInsufficient)
