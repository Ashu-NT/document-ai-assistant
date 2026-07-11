from tests.unit.application.evaluation.retrieval.benchmarking.corpus._test_retrieval_benchmark_corpus_seeder_support_part1 import *  # noqa: F401,F403

def build_document_graph(
    *,
    document_id: str,
    file_name: str,
    file_path: str,
    document_type: DocumentType,
    chunk_texts: list[str],
    question_count: int = 0,
) -> DocumentGraph:
    document = Document(
        document_id=document_id,
        file_name=file_name,
        file_path=file_path,
        hashes=DocumentHashes(
            file_hash=f"{document_id}_file_hash",
            content_hash=f"{document_id}_content_hash",
        ),
        title=file_name,
        document_type=document_type,
        statistics=DocumentStatistics(page_count=1),
    )
    graph = DocumentGraph(document=document)
    section = DocumentSection(
        section_id=f"sec_{document_id}",
        document_id=document_id,
        title="Section",
        level=1,
        section_path=["Section"],
        source=SourceLocation(page_start=1, page_end=1),
        sequence_number=1,
    )
    graph.add_section(section)

    for index, chunk_text in enumerate(chunk_texts, start=1):
        element_id = f"el_{document_id}_{index}"
        section.element_ids.append(element_id)
        graph.add_element(
            CanonicalElement(
                element_id=element_id,
                document_id=document_id,
                element_type=ElementType.TEXT,
                text=chunk_text,
                parent_section_id=section.section_id,
                reading_order=index,
                source=SourceLocation(page_start=1, page_end=1),
            )
        )
        graph.add_chunk(
            DocumentChunk(
                chunk_id=f"chunk_{document_id}_{index}",
                document_id=document_id,
                section_id=section.section_id,
                content=chunk_text,
                chunk_type=ChunkType.GENERAL,
                section_path=["Section"],
                element_ids=[element_id],
                source=SourceLocation(page_start=1, page_end=1),
                sequence_number=index,
            )
        )

    for index in range(1, question_count + 1):
        graph.questions[f"question_{document_id}_{index}"] = GeneratedQuestion(
            question_id=f"question_{document_id}_{index}",
            document_id=document_id,
            chunk_id=next(iter(graph.chunks)),
            question=f"Question {index}?",
        )

    return graph

def build_document_classification(
    *,
    document_id: str,
    document_type: DocumentType,
    confidence_score: float,
) -> DocumentClassification:
    return DocumentClassification(
        document_id=document_id,
        document_type=document_type,
        result=ClassificationResult(
            classification_id=f"classification_{document_id}",
            document_id=document_id,
            predicted_label=document_type.value,
            confidence_score=confidence_score,
            rationale="Benchmark classification.",
            evidence=["Section"],
            processing_metadata=ModelProcessingMetadata(
                model_name="qwen3:8b",
                model_type="document_classification",
                confidence=confidence_score,
            ),
        ),
    )

def build_seeder(
    *,
    dataset: RetrievalBenchmarkDataset,
    operations: list[str],
    final_graphs_by_document_id: dict[str, DocumentGraph],
    ingestion_workflow: FakeIngestionWorkflow | None = None,
    duplicate_matches: dict[str, str] | None = None,
    classifications: dict[str, DocumentClassification] | None = None,
    unit_of_work: FakeUnitOfWork | None = None,
    extraction_service: FakeExtractionService | None = None,
):
    truth_set_loader = FakeTruthSetLoader(dataset)
    classification_lookup = classifications or {}
    seeder = RetrievalBenchmarkCorpusSeeder(
        ingestion_workflow=ingestion_workflow or FakeIngestionWorkflow(),
        duplicate_detection_service=FakeDuplicateDetectionService(duplicate_matches),
        document_lookup_service=FakeDocumentLookupService(final_graphs_by_document_id),
        classification_service=FakeClassificationService(classification_lookup),
        document_classification_workflow=FakeDocumentClassificationWorkflow(
            operations,
            classification_lookup,
        ),
        truth_set_loader=truth_set_loader,
        unit_of_work=unit_of_work,
        embedding_model="test-embedding-model",
        vector_collection="test_collection",
        extraction_service=extraction_service,
    )
    return seeder, truth_set_loader

__all__ = [name for name in globals() if not name.startswith("__")]
