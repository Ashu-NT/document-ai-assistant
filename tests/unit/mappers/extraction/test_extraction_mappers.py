from src.infrastructure.db.mappers import (
    EquipmentInfoMapper,
    ExtractionResultMapper,
    MaintenanceTaskMapper,
    ManufacturerMapper,
    SparePartMapper,
)


def test_maintenance_task_mapper_round_trip(sample_maintenance_task) -> None:
    orm = MaintenanceTaskMapper.to_orm(
        sample_maintenance_task,
        extraction_id="extraction_001",
    )
    domain = MaintenanceTaskMapper.to_domain(orm)

    assert domain.task_id == sample_maintenance_task.task_id
    assert domain.title == sample_maintenance_task.title
    assert domain.interval == sample_maintenance_task.interval


def test_spare_part_mapper_round_trip(sample_spare_part) -> None:
    orm = SparePartMapper.to_orm(
        sample_spare_part,
        extraction_id="extraction_001",
    )
    domain = SparePartMapper.to_domain(orm)

    assert domain.spare_part_id == sample_spare_part.spare_part_id
    assert domain.part_number == sample_spare_part.part_number


def test_equipment_info_mapper_round_trip(sample_equipment_info) -> None:
    orm = EquipmentInfoMapper.to_orm(
        sample_equipment_info,
        extraction_id="extraction_001",
    )
    domain = EquipmentInfoMapper.to_domain(orm)

    assert domain.equipment_id == sample_equipment_info.equipment_id
    assert domain.name == sample_equipment_info.name


def test_manufacturer_mapper_round_trip(sample_manufacturer) -> None:
    orm = ManufacturerMapper.to_orm(
        sample_manufacturer,
        extraction_id="extraction_001",
    )
    domain = ManufacturerMapper.to_domain(orm)

    assert domain.manufacturer_id == sample_manufacturer.manufacturer_id
    assert domain.name == sample_manufacturer.name


def test_extraction_result_mapper_round_trip(sample_extraction_result) -> None:
    result_orm = ExtractionResultMapper.to_orm(sample_extraction_result)

    task_rows = [
        MaintenanceTaskMapper.to_orm(
            task,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for task in sample_extraction_result.maintenance_tasks
    ]

    spare_part_rows = [
        SparePartMapper.to_orm(
            part,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for part in sample_extraction_result.spare_parts
    ]

    equipment_rows = [
        EquipmentInfoMapper.to_orm(
            equipment,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for equipment in sample_extraction_result.equipment
    ]

    manufacturer_rows = [
        ManufacturerMapper.to_orm(
            manufacturer,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for manufacturer in sample_extraction_result.manufacturers
    ]

    domain = ExtractionResultMapper.to_domain(
        result_orm,
        task_rows=task_rows,
        spare_part_rows=spare_part_rows,
        equipment_rows=equipment_rows,
        manufacturer_rows=manufacturer_rows,
    )

    assert domain.extraction_id == sample_extraction_result.extraction_id
    assert domain.task_count() == 1
    assert domain.spare_part_count() == 1