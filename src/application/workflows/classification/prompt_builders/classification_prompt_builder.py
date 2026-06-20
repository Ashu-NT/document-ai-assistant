from src.application.workflows.classification.prompt_builders.chunk_classification_prompt_builder import (
    ChunkClassificationPromptBuilder,
)
from src.application.workflows.classification.prompt_builders.document_classification_prompt_builder import (
    DocumentClassificationPromptBuilder,
)
from src.domain.document import Document, DocumentChunk, DocumentGraph


class ClassificationPromptBuilder:
    document_prompt_version = DocumentClassificationPromptBuilder.prompt_version
    chunk_prompt_version = ChunkClassificationPromptBuilder.prompt_version

    def __init__(
        self,
        *,
        document_prompt_builder: DocumentClassificationPromptBuilder | None = None,
        chunk_prompt_builder: ChunkClassificationPromptBuilder | None = None,
    ) -> None:
        self.document_prompt_builder = (
            document_prompt_builder
            or DocumentClassificationPromptBuilder()
        )
        self.chunk_prompt_builder = chunk_prompt_builder or ChunkClassificationPromptBuilder()

    @property
    def prompt_version(self) -> str:
        return self.document_prompt_version

    def build_document_classification_prompt(
        self,
        document_graph: DocumentGraph | Document,
    ) -> str:
        return self.document_prompt_builder.build(document_graph)

    def build_chunk_classification_prompt(self, chunk: DocumentChunk) -> str:
        return self.chunk_prompt_builder.build(chunk)
