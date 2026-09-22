import subprocess

from src.application.evaluation.reproducibility import (
    build_evaluation_run_metadata,
    resolve_git_commit,
)
from src.application.workflows.parsing.artifact_store.parsed_artifact_key import (
    PARSED_ARTIFACT_SCHEMA_VERSION,
)


def test_resolve_git_commit_returns_none_when_git_executable_missing(monkeypatch) -> None:
    def _raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError("git not found")

    monkeypatch.setattr(subprocess, "run", _raise_file_not_found)

    assert resolve_git_commit() is None


def test_resolve_git_commit_returns_none_when_not_a_git_checkout(monkeypatch, tmp_path) -> None:
    class _FailedResult:
        returncode = 128
        stdout = ""

    monkeypatch.setattr(
        subprocess, "run", lambda *args, **kwargs: _FailedResult()
    )

    assert resolve_git_commit(cwd=tmp_path) is None


def test_resolve_git_commit_returns_commit_on_success(monkeypatch) -> None:
    class _OkResult:
        returncode = 0
        stdout = "abc123\n"

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: _OkResult())

    assert resolve_git_commit() == "abc123"


def test_build_evaluation_run_metadata_degrades_gracefully_without_git(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.application.evaluation.reproducibility.evaluation_run_metadata.resolve_git_commit",
        lambda: None,
    )

    metadata = build_evaluation_run_metadata(
        parser_name="docling",
        parser_version="2.111.0",
        conversion_fingerprint="fp-1",
    )

    assert metadata.git_commit is None
    assert metadata.parser_name == "docling"
    assert metadata.parser_version == "2.111.0"
    assert metadata.conversion_fingerprint == "fp-1"
    assert metadata.artifact_schema_version == PARSED_ARTIFACT_SCHEMA_VERSION
    assert metadata.timestamp  # non-empty ISO8601 string
    assert metadata.classification_model is None
    assert metadata.extraction_model is None
    assert metadata.embedding_model is None
    assert metadata.retrieval_configuration is None


def test_build_evaluation_run_metadata_carries_evaluation_config() -> None:
    metadata = build_evaluation_run_metadata(evaluation_config={"corpus_size": 10})

    assert metadata.evaluation_config == {"corpus_size": 10}
