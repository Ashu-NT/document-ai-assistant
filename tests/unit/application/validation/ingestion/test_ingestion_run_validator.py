from src.application.validation.ingestion import IngestionRunValidator


def test_ingestion_run_validator_accepts_valid_run(sample_ingestion_run) -> None:
    result = IngestionRunValidator().validate(sample_ingestion_run)
    assert result.is_valid


def test_ingestion_run_validator_requires_run_id(sample_ingestion_run) -> None:
    sample_ingestion_run.run_id = ""
    result = IngestionRunValidator().validate(sample_ingestion_run)
    assert not result.is_valid
    assert result.issues[0].code == "ingestion.run_id.required"


def test_ingestion_run_validator_requires_file_path(sample_ingestion_run) -> None:
    sample_ingestion_run.file_path = ""
    result = IngestionRunValidator().validate(sample_ingestion_run)
    assert not result.is_valid
    assert result.issues[0].code == "ingestion.file_path.required"


def test_ingestion_run_validator_requires_file_hash(sample_ingestion_run) -> None:
    sample_ingestion_run.file_hash = ""
    result = IngestionRunValidator().validate(sample_ingestion_run)
    assert not result.is_valid
    assert result.issues[0].code == "ingestion.file_hash.required"