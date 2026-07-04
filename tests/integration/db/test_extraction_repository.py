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
    assert db_uow.extractions.list_suppliers(document_id) == []
    assert db_uow.extractions.list_procedures(document_id) == []
    assert db_uow.extractions.list_specifications(document_id) == []
    assert db_uow.extractions.list_safety_warnings(document_id) == []
    assert db_uow.extractions.list_maintenance_intervals(document_id) == []
    assert db_uow.extractions.list_troubleshooting_entries(document_id) == []


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
    assert db_uow.extractions.list_suppliers(document_id) == []
    assert db_uow.extractions.list_procedures(document_id) == []
    assert db_uow.extractions.list_specifications(document_id) == []
    assert db_uow.extractions.list_safety_warnings(document_id) == []
    assert db_uow.extractions.list_maintenance_intervals(document_id) == []
    assert db_uow.extractions.list_troubleshooting_entries(document_id) == []


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
    assert len(loaded.suppliers) == 1
    assert len(loaded.procedures) == 1
    assert len(loaded.specifications) == 1
    assert len(loaded.safety_warnings) == 1
    assert len(loaded.maintenance_intervals) == 1
    assert len(loaded.troubleshooting_entries) == 1


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


def test_list_suppliers(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    suppliers = db_uow.extractions.list_suppliers(
        sample_extraction_result.document_id
    )

    assert len(suppliers) == 1


def test_search_manufacturers(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_manufacturers("Example Manufacturer")
    no_matches = db_uow.extractions.search_manufacturers("Nonexistent Corp")

    assert len(matches) == 1
    assert no_matches == []


def test_search_suppliers(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_suppliers("Example Supplier")
    no_matches = db_uow.extractions.search_suppliers("Nonexistent Supplier")

    assert len(matches) == 1
    assert no_matches == []


def test_search_spare_parts(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_spare_parts("HP-001")
    no_matches = db_uow.extractions.search_spare_parts("ZZ-999")

    assert len(matches) == 1
    assert no_matches == []


def test_search_equipment(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_equipment("Hydraulic Pump")
    no_matches = db_uow.extractions.search_equipment("Nonexistent Equipment")

    assert len(matches) == 1
    assert no_matches == []


def test_search_maintenance_tasks(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_maintenance_tasks("hydraulic filter")
    no_matches = db_uow.extractions.search_maintenance_tasks("Nonexistent Task")

    assert len(matches) == 1
    assert no_matches == []


def test_list_procedures(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    procedures = db_uow.extractions.list_procedures(sample_extraction_result.document_id)

    assert len(procedures) == 1


def test_list_specifications(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    specifications = db_uow.extractions.list_specifications(
        sample_extraction_result.document_id
    )

    assert len(specifications) == 1


def test_list_safety_warnings(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    safety_warnings = db_uow.extractions.list_safety_warnings(
        sample_extraction_result.document_id
    )

    assert len(safety_warnings) == 1


def test_list_maintenance_intervals(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    maintenance_intervals = db_uow.extractions.list_maintenance_intervals(
        sample_extraction_result.document_id
    )

    assert len(maintenance_intervals) == 1


def test_search_procedures(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_procedures("Install hydraulic filter")
    no_matches = db_uow.extractions.search_procedures("Nonexistent Procedure")

    assert len(matches) == 1
    assert no_matches == []


def test_search_specifications(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_specifications("Pressure rating")
    no_matches = db_uow.extractions.search_specifications("Nonexistent Parameter")

    assert len(matches) == 1
    assert no_matches == []


def test_search_safety_warnings(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_safety_warnings("Depressurize")
    no_matches = db_uow.extractions.search_safety_warnings("Nonexistent Warning")

    assert len(matches) == 1
    assert no_matches == []


def test_search_maintenance_intervals(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_maintenance_intervals("1000 operating hours")
    no_matches = db_uow.extractions.search_maintenance_intervals("Nonexistent Interval")

    assert len(matches) == 1
    assert no_matches == []


def test_list_maintenance_intervals_by_task_id(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    task_id = sample_extraction_result.maintenance_tasks[0].task_id
    intervals = db_uow.extractions.list_maintenance_intervals_by_task_id(task_id)
    no_intervals = db_uow.extractions.list_maintenance_intervals_by_task_id("no_such_task")

    assert len(intervals) == 1
    assert intervals[0].maintenance_task_id == task_id
    assert no_intervals == []


def test_list_procedures_by_equipment_id(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    equipment_id = sample_extraction_result.equipment[0].equipment_id
    procedures = db_uow.extractions.list_procedures_by_equipment_id(equipment_id)
    no_procedures = db_uow.extractions.list_procedures_by_equipment_id("no_such_equipment")

    assert len(procedures) == 1
    assert procedures[0].equipment_id == equipment_id
    assert no_procedures == []


def test_list_troubleshooting_entries(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    troubleshooting_entries = db_uow.extractions.list_troubleshooting_entries(
        sample_extraction_result.document_id
    )

    assert len(troubleshooting_entries) == 1


def test_search_troubleshooting_entries(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_troubleshooting_entries(
        "Pump fails to build pressure"
    )
    no_matches = db_uow.extractions.search_troubleshooting_entries(
        "Nonexistent Symptom"
    )

    assert len(matches) == 1
    assert no_matches == []


def test_list_troubleshooting_entries_by_equipment_id(
    db_uow, sample_extraction_result
) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    equipment_id = sample_extraction_result.equipment[0].equipment_id
    entries = db_uow.extractions.list_troubleshooting_entries_by_equipment_id(
        equipment_id
    )
    no_entries = db_uow.extractions.list_troubleshooting_entries_by_equipment_id(
        "no_such_equipment"
    )

    assert len(entries) == 1
    assert entries[0].equipment_id == equipment_id
    assert no_entries == []