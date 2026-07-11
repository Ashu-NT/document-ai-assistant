import pytest

from src.application.prompts.extraction import IdentifierExtractionPromptBuilder

from src.application.validation.extraction import ExtractionResultValidator

from src.application.workflows.extraction import ExtractionWorkflow

from src.application.workflows.extraction.batching import ExtractionChunkBatcher

from src.application.workflows.extraction.batching.extraction_table_chunk_hydrator import (
    hydrate_table_chunks,
)

from src.application.workflows.extraction.candidates import (
    ExtractionCandidateSelector,
)

from src.application.workflows.extraction.pruning.empty_entity_pruner import (
    drop_empty_entities,
    has_meaningful_entity_content,
)

from src.domain.assets import TableAsset

from src.domain.common import ChunkType

from src.domain.document import DocumentChunk, DocumentSection

from src.domain.extraction import (
    EquipmentInfo,
    ExtractionResult,
    Manufacturer,
    MaintenanceInterval,
    MaintenanceTask,
    Procedure,
    ProcedureType,
    SafetyWarning,
    SparePart,
    Specification,
    Supplier,
    TroubleshootingEntry,
)

from src.shared.exceptions import SchemaValidationError

from src.shared.execution import ActionResult

from src.shared.ids import IdGenerator

class FakeLLMService:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
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
        return self.responses.pop(0)

class FakeExtractionService:
    def __init__(self) -> None:
        self.saved_results = []
        self.replaced_results = []

    def save_extraction_result(
        self,
        result,
        activity_context=None,
    ) -> ActionResult:
        self.saved_results.append(result)
        return ActionResult(
            entity_type="document",
            entity_id=result.document_id,
        )

    def replace_extraction_result(
        self,
        result,
        activity_context=None,
    ) -> ActionResult:
        self.replaced_results.append(result)
        return ActionResult(
            entity_type="document",
            entity_id=result.document_id,
        )

class SpyExtractionResultValidator:
    def __init__(self) -> None:
        self.calls = []
        self.delegate = ExtractionResultValidator()

    def validate(self, value):
        self.calls.append(value)
        return self.delegate.validate(value)

def clone_chunk(sample_chunk, *, chunk_id: str, content: str):
    return sample_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=content,
        chunk_type=sample_chunk.chunk_type,
        section_path=sample_chunk.section_path,
        element_ids=sample_chunk.element_ids,
        table_ids=sample_chunk.table_ids,
        picture_ids=sample_chunk.picture_ids,
        source=sample_chunk.source,
        sequence_number=sample_chunk.sequence_number,
        chunk_index=sample_chunk.chunk_index,
        chunk_total=sample_chunk.chunk_total,
        embedding_text=sample_chunk.embedding_text,
    )

def make_workflow(
    fake_llm_service: FakeLLMService,
    fake_extraction_service: FakeExtractionService,
    validator: SpyExtractionResultValidator | None = None,
    **kwargs,
) -> tuple[ExtractionWorkflow, SpyExtractionResultValidator]:
    spy_validator = validator or SpyExtractionResultValidator()
    workflow_kwargs = {"max_attempts": 1, **kwargs}
    workflow_kwargs.setdefault(
        "candidate_selector",
        ExtractionCandidateSelector(llm_router=None),
    )
    workflow = ExtractionWorkflow(
        llm_service=fake_llm_service,
        extraction_service=fake_extraction_service,
        extraction_result_validator=spy_validator,
        id_generator=IdGenerator(),
        prompt_builder=IdentifierExtractionPromptBuilder(),
        extraction_model="qwen3:8b",
        confidence_threshold=0.8,
        require_human_review_default=False,
        **workflow_kwargs,
    )
    return workflow, spy_validator

def _empty_extraction_response() -> str:
    return """{
  "confidence_score": 0.8,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": []
}"""

def _make_table_chunk(sample_chunk, *, chunk_id: str, content: str, table_ids: list[str]):
    return sample_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=content,
        chunk_type=sample_chunk.chunk_type,
        section_path=sample_chunk.section_path,
        element_ids=sample_chunk.element_ids,
        table_ids=table_ids,
        picture_ids=sample_chunk.picture_ids,
        source=sample_chunk.source,
        sequence_number=sample_chunk.sequence_number,
        chunk_index=sample_chunk.chunk_index,
        chunk_total=sample_chunk.chunk_total,
        embedding_text=sample_chunk.embedding_text,
    )

__all__ = [name for name in globals() if not name.startswith("__")]
