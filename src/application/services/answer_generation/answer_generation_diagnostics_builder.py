from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.formatting.answer_format_policy import (
    ANSWER_FORMAT_POLICY_RULES_VERSION,
)
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentDecision,
)
from src.application.workflows.question_answering.answer_context.key_value_extractor import (
    KEY_VALUE_EXTRACTOR_RULES_VERSION,
)
from src.application.workflows.question_answering.answer_context.maintenance_entry_merger import (
    MAINTENANCE_ENTRY_MERGER_RULES_VERSION,
)


def build_maintenance_diagnostics(structured_context) -> dict[str, int]:
    if structured_context is None:
        return {
            "maintenance_items_found": 0,
            "maintenance_items_with_interval": 0,
            "maintenance_items_without_interval": 0,
            "maintenance_items_merged": 0,
        }
    diagnostics = structured_context.diagnostics
    return {
        "maintenance_items_found": int(
            diagnostics.get("maintenance_items_found", 0)
        ),
        "maintenance_items_with_interval": int(
            diagnostics.get("maintenance_items_with_interval", 0)
        ),
        "maintenance_items_without_interval": int(
            diagnostics.get("maintenance_items_without_interval", 0)
        ),
        "maintenance_items_merged": int(
            diagnostics.get("maintenance_items_merged", 0)
        ),
    }


def build_generation_diagnostics(
    *,
    resolved_request: AnswerGenerationRequest,
    intent_decision: AnswerIntentDecision,
    structured_context,
    maintenance_diagnostics: dict[str, int],
) -> dict[str, object]:
    return {
        "answer_intent": (
            resolved_request.answer_intent.value
            if resolved_request.answer_intent is not None
            else None
        ),
        "answer_intent_confidence": intent_decision.confidence,
        "answer_intent_reason": intent_decision.reason,
        "answer_intent_signals": intent_decision.matched_signals,
        "format_policy": (
            resolved_request.format_policy.preferred_format
            if resolved_request.format_policy is not None
            else None
        ),
        "format_policy_context_signals": (
            resolved_request.format_policy.context_signals
            if resolved_request.format_policy is not None
            else {}
        ),
        "format_policy_rules_version": ANSWER_FORMAT_POLICY_RULES_VERSION,
        "key_value_extractor_rules_version": KEY_VALUE_EXTRACTOR_RULES_VERSION,
        "maintenance_entry_merger_rules_version": MAINTENANCE_ENTRY_MERGER_RULES_VERSION,
        "structured_context_source_count": (
            structured_context.source_count if structured_context is not None else 0
        ),
        **maintenance_diagnostics,
    }
