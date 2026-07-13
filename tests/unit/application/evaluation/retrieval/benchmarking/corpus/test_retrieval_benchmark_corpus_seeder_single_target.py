from tests.unit.application.evaluation.retrieval.benchmarking.corpus._test_retrieval_benchmark_corpus_seeder_support import *  # noqa: F401,F403


def test_seed_corpus_scopes_to_requested_document_alias_only() -> None:
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
        chunk_texts=["final manual chunk"],
        question_count=1,
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
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=[],
        final_graphs_by_document_id={
            "doc_manual": final_manual,
            "doc_report": final_report,
        },
        ingestion_workflow=fake_ingestion_workflow,
        classifications=classifications,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
        document_alias="manual_alias",
    )

    assert len(fake_ingestion_workflow.calls) == 1
    assert fake_ingestion_workflow.calls[0].file_path == str(first_file)
    assert manifest.document_count == 1
    assert manifest.documents[0].document_alias == "manual_alias"
