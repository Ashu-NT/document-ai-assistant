from src.application.evaluation.retrieval.benchmarking.corpus.models import (
    RetrievalBenchmarkCorpusDocument,
)
from src.application.evaluation.retrieval.benchmarking.corpus.retrieval_benchmark_seed_target_collector import (
    _CorpusSeedTarget,
)
from src.domain.classification import DocumentClassification
from src.domain.document import DocumentGraph


def build_manifest_document(
    *,
    seed_target: _CorpusSeedTarget,
    file_hash: str,
    content_hash: str | None,
    document_graph: DocumentGraph,
    classification: DocumentClassification | None,
    seed_status: str,
    embedding_model: str | None,
    vector_collection: str | None,
) -> RetrievalBenchmarkCorpusDocument:
    result = classification.result if classification is not None else None
    return RetrievalBenchmarkCorpusDocument(
        document_alias=seed_target.document_alias,
        document_id=document_graph.document.document_id,
        file_name=seed_target.file_name,
        file_path=seed_target.file_path,
        file_hash=file_hash,
        content_hash=content_hash,
        document_type=document_graph.document.document_type.value,
        page_count=document_graph.document.statistics.page_count,
        section_count=len(document_graph.sections),
        element_count=len(document_graph.elements),
        chunk_count=len(document_graph.chunks),
        question_count=len(document_graph.questions),
        classification_label=(
            classification.document_type.value
            if classification is not None
            else None
        ),
        classification_confidence=(
            result.confidence_score
            if result is not None
            else None
        ),
        embedding_model=embedding_model,
        vector_collection=vector_collection,
        seed_status=seed_status,
    )
