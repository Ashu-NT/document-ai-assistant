def test_replace_extraction_result_deletes_prior_rows_for_document(
    db_uow,
    sample_extraction_result,
    document_id,
) -> None:
    from src.domain.extraction import ExtractionResult, MaintenanceTask

    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    replacement = ExtractionResult(
        extraction_id="extraction_002",
        document_id=document_id,
        maintenance_tasks=[
            MaintenanceTask(
                task_id="task_002",
                document_id=document_id,
                title="Inspect drive belt",
                confidence_score=0.9,
            )
        ],
        spare_parts=[],
        equipment=[],
        manufacturers=[],
        confidence_score=0.95,
    )

    db_uow.extractions.replace_extraction_result(replacement)
    db_uow.commit()

    assert (
        db_uow.extractions.get_extraction_result(sample_extraction_result.extraction_id)
        is None
    )
    reloaded = db_uow.extractions.get_extraction_result("extraction_002")
    assert reloaded is not None

    tasks = db_uow.extractions.list_maintenance_tasks(document_id)
    assert len(tasks) == 1
    assert tasks[0].task_id == "task_002"

    assert db_uow.extractions.list_spare_parts(document_id) == []
    assert db_uow.extractions.list_equipment(document_id) == []
    assert db_uow.extractions.list_manufacturers(document_id) == []


def test_delete_by_document_removes_all_extraction_rows(
    db_uow,
    sample_extraction_result,
    document_id,
) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    db_uow.extractions.delete_by_document(document_id)
    db_uow.commit()

    assert (
        db_uow.extractions.get_extraction_result(sample_extraction_result.extraction_id)
        is None
    )
    assert db_uow.extractions.list_maintenance_tasks(document_id) == []
    assert db_uow.extractions.list_spare_parts(document_id) == []
    assert db_uow.extractions.list_equipment(document_id) == []
    assert db_uow.extractions.list_manufacturers(document_id) == []


def test_save_and_load_extraction_result(
    db_uow,
    sample_extraction_result,
) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    loaded = db_uow.extractions.get_extraction_result(
        sample_extraction_result.extraction_id
    )

    assert loaded is not None
    assert loaded.extraction_id == sample_extraction_result.extraction_id
    assert len(loaded.maintenance_tasks) == 1
    assert len(loaded.spare_parts) == 1
    assert len(loaded.equipment) == 1
    assert len(loaded.manufacturers) == 1


def test_list_maintenance_tasks(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    tasks = db_uow.extractions.list_maintenance_tasks(
        sample_extraction_result.document_id
    )

    assert len(tasks) == 1


def test_list_spare_parts(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    parts = db_uow.extractions.list_spare_parts(
        sample_extraction_result.document_id
    )

    assert len(parts) == 1


def test_list_equipment(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    equipment = db_uow.extractions.list_equipment(
        sample_extraction_result.document_id
    )

    assert len(equipment) == 1


def test_list_manufacturers(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    manufacturers = db_uow.extractions.list_manufacturers(
        sample_extraction_result.document_id
    )

    assert len(manufacturers) == 1