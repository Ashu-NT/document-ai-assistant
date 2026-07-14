from tests.unit.application.evaluation.retrieval.benchmarking.corpus._test_retrieval_benchmark_corpus_seeder_support import *  # noqa: F401,F403

def test_seed_corpus_retries_extraction_for_existing_duplicate_missing_extraction(
) -> None:
    """A document that exists (chunks/classification committed) but has no
    extraction result — e.g. a prior run failed mid-batch-extraction — gets
    extraction retried in place via `IngestionWorkflow.retry_extraction`,
    not silently reused and not force-reparsed into a new document_id."""
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("duplicate", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="D-005",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_existing",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final chunk"],
        question_count=1,
    )
    file_hash = compute_hashes(file_path)[0]
    classifications = {
        "doc_existing": build_document_classification(
            document_id="doc_existing",
            document_type=DocumentType.MANUAL,
            confidence_score=0.88,
        )
    }
    operations: list[str] = []
    fake_ingestion_workflow = FakeIngestionWorkflow(
        retry_extraction_results={
            "doc_existing": IngestionResult(
                status=IngestionStatus.EXTRACTED,
                document_id="doc_existing",
                file_name=file_path.name,
            ),
        }
    )
    extraction_service = FakeExtractionService(
        documents_missing_extraction={"doc_existing"}
    )
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_existing": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications=classifications,
        extraction_service=extraction_service,
    )

    messages: list[str] = []

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
        progress_callback=messages.append,
    )

    assert extraction_service.has_extraction_result_calls == ["doc_existing"]
    assert fake_ingestion_workflow.retry_extraction_calls == ["doc_existing"]
    assert fake_ingestion_workflow.calls == []
    assert manifest.documents[0].document_id == "doc_existing"
    assert manifest.documents[0].seed_status == "extraction_retried"
    assert any("Retrying extraction for doc_existing" in message for message in messages)
    assert any(
        "[1/1] fake retry extraction for doc_existing" in message
        for message in messages
    )

def test_seed_corpus_retries_existing_duplicate_with_unresolved_extraction_chunks(
) -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("duplicate", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="D-005B",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_existing",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final chunk"],
        question_count=1,
    )
    file_hash = compute_hashes(file_path)[0]
    classifications = {
        "doc_existing": build_document_classification(
            document_id="doc_existing",
            document_type=DocumentType.MANUAL,
            confidence_score=0.88,
        )
    }
    fake_ingestion_workflow = FakeIngestionWorkflow(
        retry_extraction_results={
            "doc_existing": IngestionResult(
                status=IngestionStatus.EXTRACTED,
                document_id="doc_existing",
                file_name=file_path.name,
            ),
        }
    )
    extraction_service = FakeExtractionService(
        extraction_results_by_document_id={
            "doc_existing": SimpleNamespace(unresolved_chunk_ids=["chunk_001"])
        }
    )
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=[],
        final_graphs_by_document_id={"doc_existing": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications=classifications,
        extraction_service=extraction_service,
    )
    messages: list[str] = []

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
        progress_callback=messages.append,
    )

    assert extraction_service.has_extraction_result_calls == ["doc_existing"]
    assert extraction_service.get_document_extraction_result_calls == ["doc_existing"]
    assert fake_ingestion_workflow.retry_extraction_calls == ["doc_existing"]
    assert manifest.documents[0].seed_status == "extraction_retried"
    assert any(
        "still has 1 unresolved chunk(s). Retrying only that unresolved subset"
        in message
        for message in messages
    )


def test_seed_corpus_reuses_existing_duplicate_when_extraction_is_disabled(
) -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("duplicate", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="D-005C",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_existing",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final chunk"],
        question_count=1,
    )
    file_hash = compute_hashes(file_path)[0]
    classifications = {
        "doc_existing": build_document_classification(
            document_id="doc_existing",
            document_type=DocumentType.MANUAL,
            confidence_score=0.88,
        )
    }
    fake_ingestion_workflow = FakeIngestionWorkflow(
        extraction_enabled=False,
    )
    extraction_service = FakeExtractionService(
        documents_missing_extraction={"doc_existing"}
    )
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=[],
        final_graphs_by_document_id={"doc_existing": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications=classifications,
        extraction_service=extraction_service,
    )
    messages: list[str] = []

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
        progress_callback=messages.append,
    )

    assert extraction_service.has_extraction_result_calls == ["doc_existing"]
    assert fake_ingestion_workflow.retry_extraction_calls == []
    assert manifest.documents[0].seed_status == "reused_existing"
    assert any(
        "structured extraction is disabled by config" in message.lower()
        for message in messages
    )

def test_seed_corpus_marks_zero_chunk_document_as_needing_reparse(
) -> None:
    """A document with no extraction result, zero chunks, and no persisted
    elements cannot be repaired in place. The seeder must not call
    `retry_extraction` for it; instead it is included in the manifest as-is,
    with `chunk_count=0` and a distinguishing `seed_status`, so it stays
    visible and actionable (needs `--force-reparse`) instead of vanishing or
    crashing the batch."""
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("duplicate", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="D-006",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    zero_chunk_graph = build_document_graph(
        document_id="doc_existing",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=[],
    )
    file_hash = compute_hashes(file_path)[0]
    classifications = {
        "doc_existing": build_document_classification(
            document_id="doc_existing",
            document_type=DocumentType.MANUAL,
            confidence_score=0.88,
        )
    }
    operations: list[str] = []
    fake_ingestion_workflow = FakeIngestionWorkflow()
    extraction_service = FakeExtractionService(
        documents_missing_extraction={"doc_existing"}
    )
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_existing": zero_chunk_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications=classifications,
        extraction_service=extraction_service,
    )
    messages: list[str] = []

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
        progress_callback=messages.append,
    )

    assert fake_ingestion_workflow.retry_extraction_calls == []
    assert manifest.document_count == 1
    assert manifest.documents[0].document_id == "doc_existing"
    assert manifest.documents[0].chunk_count == 0
    assert manifest.documents[0].seed_status == "no_chunks_needs_reparse"
    assert any(
        "0 chunks" in message and "manual_alias" in message for message in messages
    )
