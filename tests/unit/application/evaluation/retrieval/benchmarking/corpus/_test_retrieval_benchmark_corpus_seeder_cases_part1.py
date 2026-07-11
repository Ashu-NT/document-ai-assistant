from tests.unit.application.evaluation.retrieval.benchmarking.corpus._test_retrieval_benchmark_corpus_seeder_support import *  # noqa: F401,F403

def test_seed_corpus_runs_workflows_and_builds_manifest_from_final_chunks(
) -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    first_file = input_directory / "manual.pdf"
    second_file = input_directory / "report.pdf"
    first_file.write_text("manual", encoding="utf-8")
    second_file.write_text("report", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="A-001",
                document_alias="manual_alias",
                file_name=first_file.name,
            ),
            build_case(
                case_id="A-002",
                document_alias="report_alias",
                file_name=second_file.name,
            ),
        ],
    )
    final_manual = build_document_graph(
        document_id="doc_manual",
        file_name=first_file.name,
        file_path=str(first_file),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final manual chunk 1", "final manual chunk 2"],
        question_count=2,
    )
    final_report = build_document_graph(
        document_id="doc_report",
        file_name=second_file.name,
        file_path=str(second_file),
        document_type=DocumentType.REPORT,
        chunk_texts=["final report chunk"],
        question_count=1,
    )
    classifications = {
        "doc_manual": build_document_classification(
            document_id="doc_manual",
            document_type=DocumentType.MANUAL,
            confidence_score=0.91,
        ),
        "doc_report": build_document_classification(
            document_id="doc_report",
            document_type=DocumentType.REPORT,
            confidence_score=0.84,
        ),
    }
    fake_ingestion_workflow = FakeIngestionWorkflow(
        results_by_path={
            str(first_file): IngestionResult(
                status=IngestionStatus.COMPLETE,
                document_id="doc_manual",
                file_name=first_file.name,
            ),
            str(second_file): IngestionResult(
                status=IngestionStatus.COMPLETE,
                document_id="doc_report",
                file_name=second_file.name,
            ),
        }
    )
    operations: list[str] = []
    unit_of_work = FakeUnitOfWork()
    seeder, truth_set_loader = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={
            "doc_manual": final_manual,
            "doc_report": final_report,
        },
        ingestion_workflow=fake_ingestion_workflow,
        classifications=classifications,
        unit_of_work=unit_of_work,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
    )

    assert truth_set_loader.calls == [truth_set_path]
    assert len(fake_ingestion_workflow.calls) == 2
    assert fake_ingestion_workflow.calls[0].file_path == str(first_file)
    assert fake_ingestion_workflow.calls[0].force is True
    assert fake_ingestion_workflow.calls[1].file_path == str(second_file)
    assert operations == []
    assert manifest.document_count == 2
    assert manifest.documents[0].document_alias == "manual_alias"
    assert manifest.documents[0].chunk_count == 2
    assert manifest.documents[0].question_count == 2
    assert manifest.documents[0].document_type == DocumentType.MANUAL.value
    assert manifest.documents[0].classification_confidence == 0.91
    assert manifest.documents[0].seed_status == "seeded_new"
    assert manifest.documents[1].document_alias == "report_alias"
    assert manifest.documents[1].chunk_count == 1
    assert manifest.documents[1].file_path == second_file

def test_seed_corpus_reuses_existing_duplicate_without_ingesting_again(
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
                case_id="D-001",
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
    unit_of_work = FakeUnitOfWork()
    fake_ingestion_workflow = FakeIngestionWorkflow()
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_existing": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications=classifications,
        unit_of_work=unit_of_work,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
    )

    assert fake_ingestion_workflow.calls == []
    assert operations == []
    assert unit_of_work.commit_calls == 0
    assert manifest.documents[0].document_id == "doc_existing"
    assert manifest.documents[0].seed_status == "reused_existing"
    assert manifest.documents[0].classification_confidence == 0.88

def test_seed_corpus_reuses_existing_duplicate_when_extraction_service_confirms_it_has_extraction(
) -> None:
    """When `extraction_service` is wired, the seeder checks
    `has_extraction_result` before reusing — but a document that DOES have
    an extraction result still takes the plain reuse path, not retry."""
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
                case_id="D-004",
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
    fake_ingestion_workflow = FakeIngestionWorkflow()
    extraction_service = FakeExtractionService(documents_missing_extraction=set())
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_existing": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications=classifications,
        extraction_service=extraction_service,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
    )

    assert extraction_service.has_extraction_result_calls == ["doc_existing"]
    assert fake_ingestion_workflow.retry_extraction_calls == []
    assert manifest.documents[0].seed_status == "reused_existing"
