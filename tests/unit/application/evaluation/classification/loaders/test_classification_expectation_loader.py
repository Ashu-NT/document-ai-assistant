import pytest

from src.application.evaluation.classification.classification_review_status import (
    ClassificationReviewStatus,
)
from src.application.evaluation.classification.loaders.classification_expectation_loader import (
    ClassificationExpectationLoader,
)
from src.application.evaluation.corpus import GoldenCorpusManifest, GoldenDocumentManifestEntry
from src.domain.common import DocumentType
from src.shared.exceptions import SchemaValidationError


def _manifest() -> GoldenCorpusManifest:
    return GoldenCorpusManifest(
        [
            GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual"),
            GoldenDocumentManifestEntry(alias="doc_b", relative_path="b.pdf", category="datasheet"),
        ]
    )


def _write(tmp_path, text: str, name: str = "classification_expectations_test.md"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


class TestBasicLoading:
    def test_loads_a_valid_case_with_explicit_fields(self, tmp_path) -> None:
        path = _write(
            tmp_path,
            """
# 1. Classification Expectations

```yaml
document_alias: doc_a
expected_document_type: manual
ambiguous: true
review_status: reviewed
notes: confirmed by a human reviewer
```
""",
        )

        cases = ClassificationExpectationLoader(manifest=_manifest()).load(path)

        assert len(cases) == 1
        case = cases[0]
        assert case.document_alias == "doc_a"
        assert case.expected_document_type == DocumentType.MANUAL
        assert case.ambiguous is True
        assert case.review_status == ClassificationReviewStatus.REVIEWED
        assert case.notes == "confirmed by a human reviewer"

    def test_defaults_review_status_to_candidate_when_omitted(self, tmp_path) -> None:
        path = _write(
            tmp_path,
            """
# 1. Classification Expectations

```yaml
document_alias: doc_a
expected_document_type: manual
```
""",
        )

        cases = ClassificationExpectationLoader(manifest=_manifest()).load(path)

        assert cases[0].review_status == ClassificationReviewStatus.CANDIDATE
        assert cases[0].ambiguous is False

    def test_skips_schema_illustration_block_with_no_alias(self, tmp_path) -> None:
        path = _write(
            tmp_path,
            """
# 1. Classification Expectations

```yaml
document_alias:
expected_document_type:
```

```yaml
document_alias: doc_a
expected_document_type: manual
```
""",
        )

        cases = ClassificationExpectationLoader(manifest=_manifest()).load(path)

        assert len(cases) == 1
        assert cases[0].document_alias == "doc_a"


class TestValidation:
    def test_rejects_duplicate_aliases(self, tmp_path) -> None:
        path = _write(
            tmp_path,
            """
# 1. Classification Expectations

```yaml
document_alias: doc_a
expected_document_type: manual
```

```yaml
document_alias: doc_a
expected_document_type: datasheet
```
""",
        )

        with pytest.raises(SchemaValidationError):
            ClassificationExpectationLoader(manifest=_manifest()).load(path)

    def test_rejects_alias_not_in_manifest(self, tmp_path) -> None:
        path = _write(
            tmp_path,
            """
# 1. Classification Expectations

```yaml
document_alias: doc_unknown_to_manifest
expected_document_type: manual
```
""",
        )

        with pytest.raises(SchemaValidationError):
            ClassificationExpectationLoader(manifest=_manifest()).load(path)

    def test_rejects_invalid_expected_document_type(self, tmp_path) -> None:
        path = _write(
            tmp_path,
            """
# 1. Classification Expectations

```yaml
document_alias: doc_a
expected_document_type: not_a_real_type
```
""",
        )

        with pytest.raises(SchemaValidationError):
            ClassificationExpectationLoader(manifest=_manifest()).load(path)

    def test_rejects_missing_expected_document_type(self, tmp_path) -> None:
        path = _write(
            tmp_path,
            """
# 1. Classification Expectations

```yaml
document_alias: doc_a
```
""",
        )

        with pytest.raises(SchemaValidationError):
            ClassificationExpectationLoader(manifest=_manifest()).load(path)

    def test_rejects_invalid_review_status(self, tmp_path) -> None:
        path = _write(
            tmp_path,
            """
# 1. Classification Expectations

```yaml
document_alias: doc_a
expected_document_type: manual
review_status: definitely_reviewed_trust_me
```
""",
        )

        with pytest.raises(SchemaValidationError):
            ClassificationExpectationLoader(manifest=_manifest()).load(path)

    def test_missing_explicit_path_raises(self, tmp_path) -> None:
        with pytest.raises(SchemaValidationError):
            ClassificationExpectationLoader(manifest=_manifest()).load(
                tmp_path / "does_not_exist.md"
            )

    def test_no_glob_matches_returns_empty_list_not_an_error(self, tmp_path, monkeypatch) -> None:
        from src.config.settings import golden_corpus_settings

        monkeypatch.setattr(golden_corpus_settings, "root_dir", str(tmp_path))

        cases = ClassificationExpectationLoader(manifest=_manifest()).load()

        assert cases == []
