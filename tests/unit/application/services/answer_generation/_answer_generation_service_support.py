from src.application.prompts.answer_generation import ANSWER_PROMPT_VERSION
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_service import (
    AnswerGenerationService,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class FakeLLMService:
    def __init__(
        self,
        response: str = '{"answer_text":"The answer is 1000 hours."}',
    ) -> None:
        self.response = response
        self.calls: list[dict] = []

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        response_schema: dict | None = None,
    ) -> str:
        self.calls.append(
            {"prompt": prompt, "model": model, "response_schema": response_schema}
        )
        return self.response


class FakePromptBuilder:
    prompt_version = ANSWER_PROMPT_VERSION

    def __init__(self) -> None:
        self.requests: list[AnswerGenerationRequest] = []

    def build(self, request: AnswerGenerationRequest) -> str:
        self.requests.append(request)
        return "PROMPT"


def _make_chunk(
    chunk_id: str = "chunk_001",
    document_id: str = "doc_001",
    content: str = "Replace hydraulic filter every 1000 operating hours.",
    citation: Citation | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=["Maintenance Schedule"],
        source=SourceLocation(page_start=5, page_end=5),
        citation=citation,
    )


def _make_table_chunk(
    *,
    chunk_id: str,
    chunk_type: ChunkType,
    content: str,
    section_path: list[str],
    page_start: int,
    page_end: int,
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=chunk_type,
        section_path=section_path,
        source=SourceLocation(page_start=page_start, page_end=page_end),
        metadata=metadata or {},
    )


def _make_citation(chunk_id: str, document_id: str = "doc_001") -> Citation:
    return Citation(
        citation_id=f"cit_{chunk_id}",
        document_id=document_id,
        chunk_id=chunk_id,
    )


def make_service(
    llm: FakeLLMService | None = None,
    model: str = "qwen3:8b",
) -> tuple[AnswerGenerationService, FakeLLMService]:
    llm = llm or FakeLLMService()
    service = AnswerGenerationService(
        llm_service=llm,
        answer_generation_model=model,
    )
    return service, llm

__all__ = [name for name in globals() if not name.startswith("__")]
