from dataclasses import replace

from src.application.validation.document import DocumentHashValidator


def test_document_hash_validator_accepts_valid_document(sample_document) -> None:
    result = DocumentHashValidator().validate(sample_document)

    assert result.is_valid


def test_document_hash_validator_requires_file_hash(
    sample_document,
) -> None:
    sample_document.hashes = replace(
        sample_document.hashes,
        file_hash="",
    )

    result = DocumentHashValidator().validate(sample_document)

    assert not result.is_valid
    assert result.issues[0].field == "file_hash"
    assert result.issues[0].code == "document.file_hash.required"

def test_document_hash_validator_requires_content_hash(
    sample_document,
) -> None:
    sample_document.hashes = replace(
        sample_document.hashes,
        content_hash="",
    )

    result = DocumentHashValidator().validate(sample_document)

    assert not result.is_valid
    assert result.issues[0].field == "content_hash"
    assert result.issues[0].code == "document.content_hash.required"