from dataclasses import dataclass, field

from src.application.services.answer_generation.formatting.answer_format_policy import (
    AnswerFormatPolicy,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentDecision,
)
from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    StructuredAnswerContext,
)
from src.domain.common import ChunkType
from src.domain.document.entities.identifier import Identifier
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


@dataclass(slots=True)
class AnswerGenerationRequest:
    question: str
    context_chunks: list[RetrievedChunk]
    query_intent: str | None = None
    retrieval_intent: str | None = None
    chunk_type_preferences: list[ChunkType] = field(default_factory=list)
    answer_intent: AnswerIntent | None = None
    # Set by a caller (e.g. QuestionAnsweringWorkflow) that already ran
    # AnswerIntentAnalyzer.analyze() to build structured_context, so
    # AnswerGenerationService doesn't repeat the exact same analyze() call
    # with a second AnswerIntentAnalyzer instance -- see
    # AnswerGenerationService._resolve_intent_decision(). Recomputing was
    # previously not just wasted work: if the two call sites ever received
    # different chunk sets (e.g. via max_context_chunks below), the second
    # computation could silently disagree with the intent that
    # structured_context's key_values/maintenance_entries were already
    # extracted for.
    answer_intent_decision: AnswerIntentDecision | None = None
    structured_context: StructuredAnswerContext | None = None
    format_policy: AnswerFormatPolicy | None = None
    route: str | None = None
    document_id: str | None = None
    require_citations: bool = True
    max_context_chunks: int | None = None
    resolved_identifiers: list[Identifier] = field(default_factory=list)
    resolved_structured_entities: list = field(default_factory=list)
