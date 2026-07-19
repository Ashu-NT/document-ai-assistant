from __future__ import annotations

from typing import Any

from src.application.langgraph.common import (
    detect_structured_entity_type,
    serialize_graph_value,
)
from src.application.langgraph.common.value_coercion import optional_str
from src.application.langgraph.nodes.retrieval_intent_decision import (
    RetrievalIntentDecision,
)
from src.application.workflows.shared.structured_evidence_deduplication import (
    deduplicate_identifiers as shared_deduplicate_identifiers,
    deduplicate_structured_entities as shared_deduplicate_structured_entities,
)
from src.domain.common import IdentifierType
from src.domain.document.entities.identifier import Identifier


def serialize_tool_result(tool_result: Any) -> dict[str, Any]:
    return {
        "success": bool(getattr(tool_result, "success", False)),
        "message": getattr(tool_result, "message", None),
        "error_code": getattr(tool_result, "error_code", None),
        "diagnostics": serialize_graph_value(
            getattr(tool_result, "diagnostics", {}) or {}
        ),
        "metadata": serialize_graph_value(getattr(tool_result, "metadata", None)),
        "data": serialize_graph_value(getattr(tool_result, "data", None)),
    }


def extract_retrieval_intent_decision(
    retrieval_result: Any,
) -> RetrievalIntentDecision | None:
    """The full retrieval-side intent classification -- winner, runner-up,
    scores, gap, confidence -- read from the serialized
    `QuestionAnsweringResult.retrieval_result.retrieval_result.query`
    fields that `RetrievalQueryAnalyzer.analyze()` persists onto
    `RetrievalQuery` (see PR 1, answering_flow_weakness_remediation_plan.md).
    One extraction, reused by every consumer that needs more than the bare
    intent string (e.g. `QueryAmbiguityDetector`, PR 3) instead of each
    reclassifying the question independently."""
    query = _extract_retrieval_query_dict(retrieval_result)
    if query is None:
        return None
    detected_intent = query.get("detected_intent")
    if not detected_intent:
        return None
    return RetrievalIntentDecision(
        intent=str(detected_intent),
        best_score=_optional_int(query.get("intent_best_score")),
        runner_up_intent=optional_str(query.get("intent_runner_up")),
        runner_up_score=_optional_int(query.get("intent_runner_up_score")),
        gap=_optional_int(query.get("intent_score_gap")),
        confidence=_optional_float(query.get("intent_confidence")),
    )


def extract_retrieval_query_intent(retrieval_result: Any) -> str | None:
    """The generic `RetrievalQueryIntent` (TABLE/MAINTENANCE/IDENTIFIER/...)
    resolved during query analysis -- a thin compatibility wrapper over
    `extract_retrieval_intent_decision()` for callers that only need the
    winner, not the full decision. This is a distinct, broader
    classification than `answer_intent` (`AnswerIntent`), and is what the
    reflection strategy registries dispatch on. Shared by
    `ReflectAnswerNode` and `RetryRetrievalNode`."""
    decision = extract_retrieval_intent_decision(retrieval_result)
    return decision.intent if decision is not None else None


def _extract_retrieval_query_dict(retrieval_result: Any) -> dict[str, Any] | None:
    if not isinstance(retrieval_result, dict):
        return None
    inner_result = retrieval_result.get("retrieval_result")
    if not isinstance(inner_result, dict):
        return None
    query = inner_result.get("query")
    return query if isinstance(query, dict) else None


def extend_trace(
    existing_trace: list[dict[str, Any]],
    trace_entry: dict[str, Any],
) -> list[dict[str, Any]]:
    return [*existing_trace, trace_entry]


def build_error(
    *,
    message: str,
    error_code: str,
    diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "message": message,
        "error_code": error_code,
        "diagnostics": serialize_graph_value(diagnostics or {}),
    }


def resolve_selected_document(state: dict[str, Any]) -> tuple[str | None, str | None]:
    document_id = state.get("document_id")
    if isinstance(document_id, str) and document_id:
        return document_id, optional_str(state.get("document_title"))

    selected_document_id = state.get("selected_document_id")
    if isinstance(selected_document_id, str) and selected_document_id:
        return selected_document_id, optional_str(state.get("selected_document_title"))

    return None, None


def format_document_options(options: list[dict[str, Any]]) -> str:
    if not options:
        return "I could not determine a matching document."

    lines = ["I found multiple matching documents. Which one do you mean?"]
    for index, option in enumerate(options, start=1):
        title = (
            option.get("display_name")
            or option.get("title")
            or option.get("file_name")
            or option.get("document_id")
            or f"Document {index}"
        )
        lines.append(f"{index}. {title}")
    return "\n".join(lines)


def deserialize_identifiers(payload: Any) -> list[Identifier]:
    identifiers: list[Identifier] = []
    if not isinstance(payload, list):
        return identifiers
    for item in payload:
        identifier = _deserialize_identifier(item)
        if identifier is not None:
            identifiers.append(identifier)
    return identifiers


def extract_identifiers_from_step_results(step_results: dict[str, Any]) -> list[Identifier]:
    identifiers: list[Identifier] = []
    if not isinstance(step_results, dict):
        return identifiers
    for step_result in step_results.values():
        if not isinstance(step_result, dict):
            continue
        raw_identifiers = (step_result.get("data") or {}).get("identifiers")
        identifiers.extend(deserialize_identifiers(raw_identifiers))
    return deduplicate_identifiers(identifiers)


def deduplicate_identifiers(identifiers: list[Identifier]) -> list[Identifier]:
    return shared_deduplicate_identifiers(identifiers, strict=True)


def resolve_structured_entities(
    tool_registry: Any,
    *,
    question: str,
    document_id: str | None,
) -> list[dict[str, Any]]:
    """Directly resolves structured-entity facts (manufacturer/supplier/
    spare_part/equipment/maintenance_task) for question text, independent
    of whether a retrieval-strategy plan or execution-plan ran. This is
    what lets the direct-answer graph routes (AnswerQuestionNode,
    RetryRetrievalNode) join structured facts the same way the planned
    route does via PlanExecutor."""
    entity_type = detect_structured_entity_type(question)
    if entity_type is None:
        return []

    tool = tool_registry.get("retrieve_structured_entities")
    if tool is None:
        return []

    from src.application.tools.retrieval.retrieve_structured_entities_tool import (
        RetrieveStructuredEntitiesRequest,
    )

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type=entity_type,
            document_id=document_id,
            query_text=question,
        )
    )
    if not result.success or not isinstance(result.data, dict):
        return []

    items = result.data.get("items") or []
    return attach_entity_type(items, entity_type)


def attach_entity_type(
    items: list[Any],
    entity_type: Any,
) -> list[dict[str, Any]]:
    """Attach ``_entity_type`` to each dict in ``items``, dropping non-dicts."""
    return [
        {**item, "_entity_type": entity_type}
        for item in items
        if isinstance(item, dict)
    ]


def deduplicate_structured_entities(
    entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return shared_deduplicate_structured_entities(entities)


def _deserialize_identifier(payload: Any) -> Identifier | None:
    if isinstance(payload, Identifier):
        return payload
    if not isinstance(payload, dict):
        return None
    try:
        return Identifier(
            identifier_id=str(payload.get("identifier_id") or ""),
            document_id=str(payload.get("document_id") or ""),
            raw_value=str(payload.get("raw_value") or ""),
            identifier_type=IdentifierType(
                str(payload.get("identifier_type") or IdentifierType.UNKNOWN.value)
            ),
            chunk_id=_optional_identifier_field(payload.get("chunk_id")),
            element_id=_optional_identifier_field(payload.get("element_id")),
            section_id=_optional_identifier_field(payload.get("section_id")),
            normalized_value=_optional_identifier_field(payload.get("normalized_value")),
            confidence_score=_optional_float(payload.get("confidence_score")),
            page_start=_optional_int(payload.get("page_start")),
            page_end=_optional_int(payload.get("page_end")),
        )
    except (TypeError, ValueError):
        return None


def _optional_identifier_field(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    return None


def _optional_float(value: Any) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None
