import json

import pytest

from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.workflows.extraction.response import ExtractionResponseParser
from src.application.workflows.extraction.specialized.specialized_extraction_batch_executor import (
    SpecializedExtractionBatchExecutor,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.common.enums import IdentifierType
from src.domain.document import DocumentChunk
from src.shared.ids import IdGenerator

# One JSON key string per entity family, exactly as it appears in that
# family's own schema text (e.g. SPECIFICATION_SCHEMA_TEXT's
# '"specifications": [') -- used below to assert a specialized prompt
# contains ONLY its own requested family's schema/guidance block.
_FAMILY_KEYS: dict[ExtractionPromptType, str] = {
    ExtractionPromptType.IDENTIFIER: '"identifiers":',
    ExtractionPromptType.MANUFACTURER: '"manufacturers":',
    ExtractionPromptType.SUPPLIER: '"suppliers":',
    ExtractionPromptType.CONTACT_POINT: '"contact_points":',
    ExtractionPromptType.EQUIPMENT: '"equipment":',
    ExtractionPromptType.SPARE_PART: '"spare_parts":',
    ExtractionPromptType.SPECIFICATION: '"specifications":',
    ExtractionPromptType.MAINTENANCE_TASK: '"maintenance_tasks":',
    ExtractionPromptType.MAINTENANCE_INTERVAL: '"maintenance_intervals":',
    ExtractionPromptType.PROCEDURE: '"procedures":',
    ExtractionPromptType.SAFETY_WARNING: '"safety_warnings":',
    ExtractionPromptType.TROUBLESHOOTING: '"troubleshooting_entries":',
}


class FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        activity_context=None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict | None = None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "temperature": temperature,
                "json_mode": json_mode,
                "response_schema": response_schema,
            }
        )
        return self.response


def _make_chunk(chunk_id: str, content: str, chunk_type: ChunkType) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content=content,
        chunk_type=chunk_type,
        section_path=["General"],
        source=SourceLocation(page_start=1, page_end=1),
    )


def _make_batch(chunks: list[DocumentChunk]) -> ExtractionBatch:
    return ExtractionBatch(
        batch_index=1,
        batch_count=1,
        chunks=chunks,
        char_count=sum(len(chunk.content) for chunk in chunks),
        word_count=sum(len(chunk.content.split()) for chunk in chunks),
    )


def _make_assembler() -> ExtractionResultAssembler:
    support = ExtractionBuilderSupport(
        confidence_threshold=0.5, require_human_review_default=False
    )
    return ExtractionResultAssembler(
        id_generator=IdGenerator(),
        response_parser=ExtractionResponseParser(),
        support=support,
    )


def _make_executor(
    entity_type: ExtractionPromptType, llm_service: FakeLLMService
) -> SpecializedExtractionBatchExecutor:
    return SpecializedExtractionBatchExecutor(
        entity_type=entity_type,
        llm_service=llm_service,
        extraction_model="qwen2.5:3b",
        temperature=0.0,
        json_mode=True,
        failure_preview_chars=500,
        result_assembler=_make_assembler(),
    )


@pytest.mark.parametrize(
    "entity_type",
    [
        ExtractionPromptType.SPECIFICATION,
        ExtractionPromptType.PROCEDURE,
        ExtractionPromptType.MAINTENANCE_TASK,
        ExtractionPromptType.SAFETY_WARNING,
        ExtractionPromptType.IDENTIFIER,
    ],
)
def test_specialized_call_contains_only_its_own_family_schema_and_guidance(
    entity_type: ExtractionPromptType,
) -> None:
    chunk = _make_chunk("c1", "Some generic chunk content.", ChunkType.GENERAL)
    batch = _make_batch([chunk])
    llm_service = FakeLLMService(response='{"confidence_score": 0.9}')
    executor = _make_executor(entity_type, llm_service)

    executor.execute_once(
        document_id="doc_001",
        batch=batch,
        activity_context=None,
        progress_callback=None,
        previous_error=None,
        diagnostics_sink=[],
    )

    prompt = llm_service.calls[0]["prompt"]
    assert isinstance(prompt, str)
    assert _FAMILY_KEYS[entity_type] in prompt
    for other_entity_type, other_key in _FAMILY_KEYS.items():
        if other_entity_type is entity_type:
            continue
        assert other_key not in prompt, (
            f"{entity_type.value} prompt unexpectedly contained "
            f"{other_entity_type.value}'s schema key {other_key!r}"
        )


def test_identifier_specialized_call_uses_the_live_identifier_type_vocabulary() -> None:
    chunk = _make_chunk("c1", "Part number HP-001.", ChunkType.GENERAL)
    batch = _make_batch([chunk])
    llm_service = FakeLLMService(response='{"confidence_score": 0.9}')
    executor = _make_executor(ExtractionPromptType.IDENTIFIER, llm_service)

    executor.execute_once(
        document_id="doc_001",
        batch=batch,
        activity_context=None,
        progress_callback=None,
        previous_error=None,
        diagnostics_sink=[],
    )

    prompt = llm_service.calls[0]["prompt"]
    for member in IdentifierType:
        assert member.value in prompt


def test_specialized_executor_accepts_a_single_family_only_json_response() -> None:
    # ExtractionResponsePayload gives every family field a default, so a
    # response naming ONLY the requested family must parse and build
    # successfully with zero parser/builder changes.
    chunk = _make_chunk(
        "c1", "Tank Capacity is 1200 L.", ChunkType.TECHNICAL_SPECIFICATION
    )
    batch = _make_batch([chunk])
    response = json.dumps(
        {
            "confidence_score": 0.9,
            "specifications": [
                {
                    "parameter": "Tank Capacity",
                    "value": "1200",
                    "unit": "L",
                    "source_chunk_id": "c1",
                }
            ],
        }
    )
    llm_service = FakeLLMService(response=response)
    executor = _make_executor(ExtractionPromptType.SPECIFICATION, llm_service)

    result = executor.execute_once(
        document_id="doc_001",
        batch=batch,
        activity_context=None,
        progress_callback=None,
        previous_error=None,
        diagnostics_sink=[],
    )

    assert len(result.specifications) == 1
    assert result.specifications[0].parameter == "Tank Capacity"
    assert not result.maintenance_tasks
    assert not result.safety_warnings
