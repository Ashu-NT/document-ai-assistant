from src.infrastructure.db.mappers import (
    IngestionRunMapper,
)


def test_ingestion_run_mapper_round_trip(sample_ingestion_run) -> None:
    orm = IngestionRunMapper.to_orm(sample_ingestion_run)
    domain = IngestionRunMapper.to_domain(orm)

    assert domain.run_id == sample_ingestion_run.run_id
    assert domain.file_path == sample_ingestion_run.file_path
    assert domain.file_hash == sample_ingestion_run.file_hash
    assert domain.status == sample_ingestion_run.status