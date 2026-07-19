from src.application.prompts.answer_generation import ANSWER_PROMPT_VERSION
from src.application.services.answer_generation.answer_generation_response_schema import (
    AnswerGenerationResponsePayload,
    AnswerSectionPayload,
    ReferenceNotePayload,
)
from src.application.services.answer_generation.answer_generation_result import (
    AnswerSection,
    GeneratedAnswer,
    ReferenceNote,
)
from src.domain.common.processing_metadata import ModelProcessingMetadata
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class AnswerGenerationResultAssembler:
    def build(
        self,
        *,
        answer_text: str,
        context_chunks: list[RetrievedChunk],
        prompt_version: str,
        model_name: str,
        answer_intent,
        confidence: float,
        diagnostics: dict[str, object],
        raw_model_output: str,
        limitation_note: str | None = None,
        payload: AnswerGenerationResponsePayload | None = None,
        sources=(),
        appendix_source_numbers: set[int] | None = None,
    ) -> GeneratedAnswer:
        citations, cited_chunk_ids = self._build_citations(context_chunks)
        sections = self._resolve_sections(payload.sections) if payload is not None else []
        reference_notes = (
            self._resolve_reference_notes(
                payload.reference_notes,
                sources,
                appendix_source_numbers=appendix_source_numbers,
            )
            if payload is not None
            else []
        )
        return GeneratedAnswer(
            answer_text=answer_text,
            citations=citations,
            cited_chunk_ids=cited_chunk_ids,
            prompt_version=prompt_version or ANSWER_PROMPT_VERSION,
            model_name=model_name,
            confidence=confidence,
            metadata=ModelProcessingMetadata(
                model_name=model_name,
                model_type="answer_generation",
                confidence=confidence,
                prompt_version=prompt_version or ANSWER_PROMPT_VERSION,
            ),
            answer_intent=answer_intent,
            diagnostics=diagnostics,
            raw_model_output=raw_model_output,
            limitation_note=limitation_note,
            sections=sections,
            reference_notes=reference_notes,
        )

    @staticmethod
    def _resolve_sections(
        payload_sections: list[AnswerSectionPayload],
    ) -> list[AnswerSection]:
        return [
            AnswerSection(
                heading=section.heading,
                body=section.body,
                reference_note_ids=list(section.reference_note_ids),
            )
            for section in payload_sections
        ]

    @staticmethod
    def _resolve_reference_notes(
        payload_notes: list[ReferenceNotePayload],
        sources,
        *,
        appendix_source_numbers: set[int] | None = None,
    ) -> list[ReferenceNote]:
        chunk_id_by_source_number = {
            source.source_number: source.chunk_id
            for source in sources
            if appendix_source_numbers is None
            or source.source_number in appendix_source_numbers
        }
        return [
            ReferenceNote(
                note_id=note.note_id,
                claim_text=note.claim_text,
                source_number=note.source_number,
                chunk_id=chunk_id_by_source_number.get(note.source_number),
            )
            for note in payload_notes
        ]

    @staticmethod
    def _build_citations(
        chunks: list[RetrievedChunk],
    ) -> tuple[list[Citation], list[str]]:
        citations: list[Citation] = []
        cited_chunk_ids: list[str] = []
        for chunk in chunks:
            if chunk.citation is not None:
                citations.append(chunk.citation)
                cited_chunk_ids.append(chunk.chunk_id)
        return citations, cited_chunk_ids
