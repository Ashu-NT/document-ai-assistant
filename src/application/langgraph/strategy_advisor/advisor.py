from __future__ import annotations

from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorEvent,
    StrategyAdvisorOutcome,
    StrategyAdvisorRequest,
    StrategyAdvisorStatus,
)
from src.application.langgraph.strategy_advisor.advisor_prompt_builder import (
    StrategyAdvisorPromptBuilder,
)
from src.application.langgraph.strategy_advisor.advisor_validator import (
    StrategyAdvisorValidator,
)
from src.application.services.ai import LLMService
from src.shared.exceptions import ApplicationError, SchemaValidationError


class StrategyAdvisor:
    def __init__(
        self,
        llm_service: LLMService,
        *,
        prompt_builder: StrategyAdvisorPromptBuilder | None = None,
        validator: StrategyAdvisorValidator | None = None,
        model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.prompt_builder = prompt_builder or StrategyAdvisorPromptBuilder()
        self.validator = validator or StrategyAdvisorValidator()
        self.model = model

    def trigger_reason(self, request: StrategyAdvisorRequest) -> str | None:
        normalized = f" {request.query_text.strip().lower()} "
        if request.deterministic_route == "deep_research":
            return "deep_research_route"
        if request.deterministic_route_confidence < 0.8:
            return "low_deterministic_confidence"
        if any(marker in normalized for marker in _COMPARE_MARKERS):
            return "comparison_or_relationship_request"
        if " and " in normalized and len(request.deterministic_strategies) != 1:
            return "multi_intent_request"
        if len(request.deterministic_strategies) > 1:
            return "ambiguous_multi_strategy_request"
        return request.trigger_reason

    def advise(self, request: StrategyAdvisorRequest) -> StrategyAdvisorOutcome:
        events = [
            StrategyAdvisorEvent(
                name="StrategyAdvisorStarted",
                message="Running guarded strategy advisor.",
                diagnostics={"trigger_reason": request.trigger_reason},
            )
        ]
        prompt = self.prompt_builder.build(request)
        try:
            raw_response = self.llm_service.generate(prompt, model=self.model)
            proposal = self.validator.validate_response(raw_response, request=request)
        except (ApplicationError, SchemaValidationError, ValueError) as exc:
            events.append(
                StrategyAdvisorEvent(
                    name="StrategyAdvisorRejected",
                    message="Strategy advisor proposal was rejected.",
                    diagnostics={"reason": str(exc)},
                )
            )
            return StrategyAdvisorOutcome(
                status=StrategyAdvisorStatus.REJECTED,
                reason=str(exc),
                diagnostics={"trigger_reason": request.trigger_reason},
                events=events,
            )
        except Exception as exc:
            events.append(
                StrategyAdvisorEvent(
                    name="StrategyAdvisorRejected",
                    message="Strategy advisor failed unexpectedly and fell back to deterministic logic.",
                    diagnostics={"reason": str(exc)},
                )
            )
            return StrategyAdvisorOutcome(
                status=StrategyAdvisorStatus.REJECTED,
                reason=str(exc),
                diagnostics={"trigger_reason": request.trigger_reason},
                events=events,
            )
        events.append(
            StrategyAdvisorEvent(
                name="StrategyAdvisorCompleted",
                message="Strategy advisor returned a structured proposal.",
                diagnostics={
                    "route": proposal.route,
                    "intent": proposal.intent.value,
                    "concept_count": len(proposal.concepts),
                },
            )
        )
        events.append(
            StrategyAdvisorEvent(
                name="StrategyValidated",
                message="Strategy advisor proposal passed deterministic validation.",
                diagnostics={
                    "route": proposal.route,
                    "strategies": [
                        strategy.value for strategy in proposal.recommended_strategies
                    ],
                },
            )
        )
        return StrategyAdvisorOutcome(
            status=StrategyAdvisorStatus.ACCEPTED,
            proposal=proposal,
            diagnostics={"trigger_reason": request.trigger_reason},
            events=events,
        )


_COMPARE_MARKERS = (
    " compare ",
    " contrast ",
    " difference between ",
    " differences between ",
    " relationship between ",
    " relate ",
    " versus ",
    " vs ",
)

