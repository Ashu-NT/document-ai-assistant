from typing import TYPE_CHECKING

__all__ = [
    "AnswerFormatPolicy",
    "AnswerGenerationRequest",
    "AnswerGenerationService",
    "AnswerIntent",
    "AnswerIntentAnalyzer",
    "AnswerIntentDecision",
    "GeneratedAnswer",
]

if TYPE_CHECKING:
    from src.application.services.answer_generation.formatting.policy.answer_format_policy import (
        AnswerFormatPolicy,
    )
    from src.application.services.answer_generation.answer_generation_request import (
        AnswerGenerationRequest,
    )
    from src.application.services.answer_generation.answer_generation_service import (
        AnswerGenerationService,
    )
    from src.application.services.answer_generation.intent.answer_intent import (
        AnswerIntent,
    )
    from src.application.services.answer_generation.intent.answer_intent_analyzer import (
        AnswerIntentAnalyzer,
        AnswerIntentDecision,
    )
    from src.application.services.answer_generation.answer_generation_result import (
        GeneratedAnswer,
    )


def __getattr__(name: str):
    if name == "AnswerFormatPolicy":
        from src.application.services.answer_generation.formatting.policy.answer_format_policy import (
            AnswerFormatPolicy,
        )

        return AnswerFormatPolicy
    if name == "AnswerGenerationRequest":
        from src.application.services.answer_generation.answer_generation_request import (
            AnswerGenerationRequest,
        )

        return AnswerGenerationRequest
    if name == "AnswerGenerationService":
        from src.application.services.answer_generation.answer_generation_service import (
            AnswerGenerationService,
        )

        return AnswerGenerationService
    if name == "AnswerIntent":
        from src.application.services.answer_generation.intent.answer_intent import (
            AnswerIntent,
        )

        return AnswerIntent
    if name == "AnswerIntentAnalyzer":
        from src.application.services.answer_generation.intent.answer_intent_analyzer import (
            AnswerIntentAnalyzer,
        )

        return AnswerIntentAnalyzer
    if name == "AnswerIntentDecision":
        from src.application.services.answer_generation.intent.answer_intent_analyzer import (
            AnswerIntentDecision,
        )

        return AnswerIntentDecision
    if name == "GeneratedAnswer":
        from src.application.services.answer_generation.answer_generation_result import (
            GeneratedAnswer,
        )

        return GeneratedAnswer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
