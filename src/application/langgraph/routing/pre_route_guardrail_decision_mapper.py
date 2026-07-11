from __future__ import annotations

from src.application.guardrails import GuardrailDecision
from src.application.langgraph.routing.route_decision import RouteDecision
from src.application.langgraph.routing.route_type import RouteType


def map_guardrail_decision(
    *,
    result,
    user_input: str,
    extracted_document_query: str | None,
) -> RouteDecision:
    options = {
        "guardrail_decision": result.decision.value,
        "guardrail_reason": result.reason,
        "guardrail_user_message": result.user_message,
        "guardrail_result": result.to_dict(),
        "guardrail_trace_id": result.trace_id,
        "guardrail_trace": result.diagnostics.get("guardrail_trace", []),
        "blocked_tools": list(result.blocked_tools),
    }
    violations = result.violations
    if violations:
        first_violation = violations[0]
        options["blocked_terms"] = list(first_violation.matched_terms)
        options["blocked_severity"] = (
            first_violation.severity.value
            if first_violation.severity is not None
            else result.severity.value
        )
    if result.decision in {
        GuardrailDecision.REDIRECT,
        GuardrailDecision.OUT_OF_SCOPE,
    }:
        return RouteDecision(
            route_type=RouteType.OUT_OF_SCOPE,
            confidence=1.0,
            reason=result.reason,
            extracted_document_query=extracted_document_query,
            extracted_question=user_input.strip(),
            options=options,
        )
    if result.decision in {
        GuardrailDecision.CLARIFY,
        GuardrailDecision.NEEDS_CLARIFICATION,
    }:
        return RouteDecision(
            route_type=RouteType.NEEDS_CLARIFICATION,
            confidence=0.95,
            reason=result.reason,
            extracted_document_query=extracted_document_query,
            extracted_question=user_input.strip(),
            options=options,
        )
    options["unsafe_request_blocked"] = (
        result.diagnostics.get("scope_category") == "unsafe_destructive"
    )
    options["blocked_reason"] = result.reason
    return RouteDecision(
        route_type=RouteType.BLOCKED_ACTION,
        confidence=1.0,
        reason=result.reason,
        extracted_document_query=extracted_document_query,
        extracted_question=user_input.strip(),
        options=options,
    )
