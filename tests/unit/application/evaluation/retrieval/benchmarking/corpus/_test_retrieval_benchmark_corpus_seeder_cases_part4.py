from tests.unit.application.evaluation.retrieval.benchmarking.corpus._test_retrieval_benchmark_corpus_seeder_support import *  # noqa: F401,F403

def test_seed_corpus_force_reparses_existing_duplicate_via_ingestion_workflow() -> None:
    """--force-reparse routes through the canonical IngestionWorkflow, same as a
    genuinely new document. IngestionRequest has no way to target an existing
    document_id (and reusing one would mean re-running extraction against it,
    which is unsafe today - extraction results are not replaced atomically),
    so a forced reseed always produces a *new* document_id. The old
    document_id is left in place, orphaned, since safe delete isn't supported
    yet either - that's tracked as a known, accepted limitation, not silently
    swept under the rug."""
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
                case_id="D-003",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_new",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final chunk"],
        question_count=1,
    )
    file_hash = compute_hashes(file_path)[0]
    classification = build_document_classification(
        document_id="doc_new",
        document_type=DocumentType.MANUAL,
        confidence_score=0.92,
    )
    operations: list[str] = []
    unit_of_work = FakeUnitOfWork()
    fake_ingestion_workflow = FakeIngestionWorkflow(
        results_by_path={
            str(file_path): IngestionResult(
                status=IngestionStatus.COMPLETE,
                document_id="doc_new",
                file_name=file_path.name,
            ),
        }
    )
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_new": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications={"doc_new": classification},
        unit_of_work=unit_of_work,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
        force_reparse_existing=True,
    )

    assert len(fake_ingestion_workflow.calls) == 1
    assert fake_ingestion_workflow.calls[0].file_path == str(file_path)
    assert fake_ingestion_workflow.calls[0].force is True
    assert operations == []
    # a genuinely new document_id, distinct from the stale "doc_existing"
    assert manifest.documents[0].document_id == "doc_new"
    assert manifest.documents[0].seed_status == "reseeded_new"

def test_seed_corpus_rejects_conflicting_alias_mapping() -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    (input_directory / "first.pdf").write_text("first", encoding="utf-8")
    (input_directory / "second.pdf").write_text("second", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="C-001",
                document_alias="manual_alias",
                file_name="first.pdf",
            ),
            build_case(
                case_id="C-002",
                document_alias="manual_alias",
                file_name="second.pdf",
            ),
        ],
    )
    operations: list[str] = []
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={},
        classifications={},
    )

    with pytest.raises(SchemaValidationError):
        seeder.seed_corpus(
            truth_set_path=truth_set_path,
            input_directory=input_directory,
        )

def test_seed_corpus_fails_when_expected_file_is_missing() -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="M-001",
                document_alias="manual_alias",
                file_name="missing.pdf",
            )
        ],
    )
    operations: list[str] = []
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={},
        classifications={},
    )

    with pytest.raises(SchemaValidationError):
        seeder.seed_corpus(
            truth_set_path=truth_set_path,
            input_directory=input_directory,
        )

def test_seed_corpus_emits_progress_messages_for_major_stages() -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("manual", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="P-001",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_manual",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final manual chunk"],
        question_count=1,
    )
    classifications = {
        "doc_manual": build_document_classification(
            document_id="doc_manual",
            document_type=DocumentType.MANUAL,
            confidence_score=0.9,
        )
    }
    fake_ingestion_workflow = FakeIngestionWorkflow(
        results_by_path={
            str(file_path): IngestionResult(
                status=IngestionStatus.COMPLETE,
                document_id="doc_manual",
                file_name=file_path.name,
            ),
        }
    )
    operations: list[str] = []
    unit_of_work = FakeUnitOfWork()
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_manual": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        classifications=classifications,
        unit_of_work=unit_of_work,
    )
    messages: list[str] = []

    seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
        progress_callback=messages.append,
    )

    assert any("Loading retrieval benchmark truth set" in message for message in messages)
    assert any("Computing hashes" in message for message in messages)
    assert any("File size:" in message for message in messages)
    assert any("Delegating to canonical IngestionWorkflow" in message for message in messages)
    assert any("fake ingestion for" in message for message in messages)
    assert any("Corpus seeding completed for 1 document(s)." in message for message in messages)
