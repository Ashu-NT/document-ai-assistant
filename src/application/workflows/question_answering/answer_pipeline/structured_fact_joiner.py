from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
    AnswerIntentDecision,
)
from src.application.services.document import DocumentLookupService
from src.application.workflows.question_answering.answer_context.answer_context_organizer import (
    AnswerContextOrganizer,
)
from src.application.workflows.question_answering.answer_context import (
    StructuredAnswerContext,
)
from src.application.workflows.question_answering.answer_context.structured_evidence_view_builder import (
    StructuredEvidenceViewBuilder,
)
from src.application.workflows.question_answering.answer_context.structured_fact_key_value_builder import (
    StructuredFactKeyValueBuilder,
)
from src.application.workflows.question_answering.answer_pipeline.retrieved_chunk_converter import (
    to_retrieved_chunk,
)
from src.application.workflows.question_answering.evidence import FinalEvidencePreparer
from src.application.workflows.question_answering.question_answering_route import (
    QuestionAnsweringRoute,
)
from src.domain.retrieval import RetrievalQuery
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class StructuredFactJoiner:
    """Joins resolved identifiers/structured-entity rows to the same
    chunk-based context used for generation, fetching their exact source
    chunk when normal retrieval didn't already surface it, so these facts
    reach the LLM as real evidence instead of only reaching the user
    through a deterministic bypass renderer."""

    def __init__(
        self,
        *,
        document_lookup_service: DocumentLookupService | None,
        final_evidence_preparer: FinalEvidencePreparer,
        answer_context_organizer: AnswerContextOrganizer,
        structured_fact_key_value_builder: StructuredFactKeyValueBuilder,
        structured_evidence_view_builder: StructuredEvidenceViewBuilder,
        answer_intent_analyzer: AnswerIntentAnalyzer,
    ) -> None:
        self._document_lookup_service = document_lookup_service
        self._final_evidence_preparer = final_evidence_preparer
        self._answer_context_organizer = answer_context_organizer
        self._structured_fact_key_value_builder = structured_fact_key_value_builder
        self._structured_evidence_view_builder = structured_evidence_view_builder
        self._answer_intent_analyzer = answer_intent_analyzer

    def join(
        self,
        *,
        approved_chunks: list[RetrievedChunk],
        analyzed_query: RetrievalQuery,
        question: str,
        resolved_identifiers: list,
        resolved_structured_entities: list,
    ) -> tuple[
        list[RetrievedChunk],
        StructuredAnswerContext | None,
        AnswerIntentDecision | None,
    ]:
        existing_chunk_ids = {chunk.chunk_id for chunk in approved_chunks}
        needed_chunk_ids: set[str] = set()
        for identifier in resolved_identifiers:
            chunk_id = identifier.chunk_id
            if chunk_id and chunk_id not in existing_chunk_ids:
                needed_chunk_ids.add(chunk_id)
        for entity in resolved_structured_entities:
            if not isinstance(entity, dict):
                continue
            chunk_id = entity.get("source_chunk_id")
            if chunk_id and chunk_id not in existing_chunk_ids:
                needed_chunk_ids.add(chunk_id)
            for related in entity.get("related_entities", []):
                if not isinstance(related, dict):
                    continue
                related_entity = related.get("entity")
                if not isinstance(related_entity, dict):
                    continue
                related_chunk_id = related_entity.get("source_chunk_id")
                if related_chunk_id and related_chunk_id not in existing_chunk_ids:
                    needed_chunk_ids.add(related_chunk_id)

        joined_chunks = list(approved_chunks)
        if needed_chunk_ids and self._document_lookup_service is not None:
            fetched_chunks = self._document_lookup_service.get_chunks_by_ids(
                list(needed_chunk_ids)
            )
            joined_chunks.extend(to_retrieved_chunk(chunk) for chunk in fetched_chunks)

        prepared_chunks = self._final_evidence_preparer.prepare(
            query=analyzed_query,
            chunks=joined_chunks,
        )

        if not resolved_identifiers and not resolved_structured_entities:
            return prepared_chunks, None, None

        intent_decision = self._resolve_structured_answer_intent_decision(
            question=question,
            analyzed_query=analyzed_query,
            prepared_chunks=prepared_chunks,
        )
        structured_context = self._answer_context_organizer.organize(
            answer_intent=intent_decision.intent,
            chunks=prepared_chunks,
        )
        source_number_by_chunk_id = self._source_number_by_chunk_id(
            chunks=prepared_chunks,
            structured_context=structured_context,
        )

        extra_key_values = (
            self._structured_fact_key_value_builder.build_from_identifiers(
                list(resolved_identifiers),
                source_number_by_chunk_id=source_number_by_chunk_id,
            )
        )
        entities_by_type: dict[str, list[dict]] = {}
        for entity in resolved_structured_entities:
            if not isinstance(entity, dict):
                continue
            entity_type = entity.get("_entity_type")
            if not entity_type:
                continue
            entities_by_type.setdefault(entity_type, []).append(entity)
        for entity_type, entities in entities_by_type.items():
            extra_key_values.extend(
                self._structured_fact_key_value_builder.build_from_structured_entities(
                    entity_type,
                    entities,
                    source_number_by_chunk_id=source_number_by_chunk_id,
                )
            )

        # Always keep structured_context once it was successfully organized
        # -- previously this returned None whenever extra_key_values was
        # empty (e.g. a resolved entity's source chunk couldn't be fetched),
        # silently discarding the organized sources/groups/maintenance
        # entries even though prepared_chunks existed (closes 4.3/9.7).
        structured_context.key_values.extend(extra_key_values)
        structured_context.structured_entities.extend(
            self._structured_evidence_view_builder.build(
                list(resolved_structured_entities)
            )
        )
        return prepared_chunks, structured_context, intent_decision

    def _resolve_structured_answer_intent_decision(
        self,
        *,
        question: str,
        analyzed_query: RetrievalQuery,
        prepared_chunks: list[RetrievedChunk],
    ) -> AnswerIntentDecision:
        return self._answer_intent_analyzer.analyze(
            question=question,
            retrieval_intent=analyzed_query.detected_intent,
            chunk_type_preferences=analyzed_query.chunk_types,
            approved_chunks=prepared_chunks,
            legacy_query_intent=analyzed_query.detected_intent,
            route=QuestionAnsweringRoute.RETRIEVAL_QA.value,
        )

    @staticmethod
    def _source_number_by_chunk_id(
        *,
        chunks: list[RetrievedChunk],
        structured_context: StructuredAnswerContext,
    ) -> dict[str, int]:
        chunk_by_id = {chunk.chunk_id: chunk for chunk in chunks}
        source_numbers: dict[str, int] = {}

        for source in structured_context.sources:
            source_numbers[source.chunk_id] = source.source_number
            chunk = chunk_by_id.get(source.chunk_id)
            if chunk is None:
                continue

            collapsed_chunk_ids = chunk.metadata.get("dedup_collapsed_chunk_ids", "")
            for collapsed_chunk_id in collapsed_chunk_ids.split(","):
                normalized_chunk_id = collapsed_chunk_id.strip()
                if normalized_chunk_id:
                    source_numbers[normalized_chunk_id] = source.source_number

        return source_numbers
