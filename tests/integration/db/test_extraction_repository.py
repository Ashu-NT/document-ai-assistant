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