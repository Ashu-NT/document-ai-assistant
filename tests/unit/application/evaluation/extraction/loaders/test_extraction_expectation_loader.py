import pytest

from src.application.evaluation.corpus.evaluation_corpus_tier import (
    EvaluationCorpusTier,
)
from src.application.evaluation.corpus.golden_corpus_manifest import (
    GoldenCorpusManifest,
)
from src.application.evaluation.corpus.golden_document_manifest_entry import (
    GoldenDocumentManifestEntry,
)
from src.application.evaluation.extraction.loaders.extraction_expectation_loader import (
    ExtractionExpectationLoader,
)
from src.shared.exceptions import SchemaValidationError


def _manifest() -> GoldenCorpusManifest:
    return GoldenCorpusManifest(
        entries=(
            GoldenDocumentManifestEntry(
                alias="doc_a",
                relative_path="doc_a.pdf",
                category="test",
                tier=EvaluationCorpusTier.CORE,
            ),
        )
    )


def _write(tmp_path, text: str, name: str = "extraction_expectations_test.md"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


class TestBasicLoading:
    def test_loads_one_expectation_and_skips_schema_block(self, tmp_path) -> None:
        text = """\
# 1. Test

```yaml
kind:
case_id:
```

```yaml
kind: expectation
case_id: e1
document_alias: doc_a
entity_type: manufacturer
scope_type: whole_document
expected_fields:
  name: Acme
```
"""
        path = _write(tmp_path, text)
        truth_set = ExtractionExpectationLoader(manifest=_manifest()).load(path)

        assert len(truth_set.expectations) == 1
        case = truth_set.expectations[0]
        assert case.case_id == "e1"
        assert case.document_alias == "doc_a"
        assert case.expected_fields == {"name": "Acme"}

    def test_loads_applicability_declaration(self, tmp_path) -> None:
        text = """\
# 1. Test

```yaml
kind: applicability
declaration_id: a1
document_alias: doc_a
entity_type: maintenance_interval
scope_type: whole_document
applicability: not_applicable
reason: stated elsewhere
```
"""
        path = _write(tmp_path, text)
        truth_set = ExtractionExpectationLoader(manifest=_manifest()).load(path)

        assert len(truth_set.applicability_declarations) == 1
        assert truth_set.applicability_declarations[0].reason == "stated elsewhere"

    def test_missing_file_raises(self, tmp_path) -> None:
        with pytest.raises(SchemaValidationError):
            ExtractionExpectationLoader(manifest=_manifest()).load(tmp_path / "nope.md")

    def test_unknown_document_alias_raises(self, tmp_path) -> None:
        text = """\
# 1. Test

```yaml
kind: expectation
case_id: e1
document_alias: unknown_doc
entity_type: manufacturer
scope_type: whole_document
expected_fields:
  name: Acme
```
"""
        path = _write(tmp_path, text)
        with pytest.raises(SchemaValidationError):
            ExtractionExpectationLoader(manifest=_manifest()).load(path)

    def test_invalid_entity_type_raises(self, tmp_path) -> None:
        text = """\
# 1. Test

```yaml
kind: expectation
case_id: e1
document_alias: doc_a
entity_type: not_a_real_entity_type
scope_type: whole_document
```
"""
        path = _write(tmp_path, text)
        with pytest.raises(SchemaValidationError):
            ExtractionExpectationLoader(manifest=_manifest()).load(path)

    def test_page_range_without_bounds_raises(self, tmp_path) -> None:
        text = """\
# 1. Test

```yaml
kind: expectation
case_id: e1
document_alias: doc_a
entity_type: manufacturer
scope_type: page_range
```
"""
        path = _write(tmp_path, text)
        with pytest.raises(SchemaValidationError):
            ExtractionExpectationLoader(manifest=_manifest()).load(path)

    def test_not_applicable_without_reason_raises(self, tmp_path) -> None:
        text = """\
# 1. Test

```yaml
kind: applicability
declaration_id: a1
document_alias: doc_a
entity_type: maintenance_interval
scope_type: whole_document
applicability: not_applicable
```
"""
        path = _write(tmp_path, text)
        with pytest.raises(SchemaValidationError):
            ExtractionExpectationLoader(manifest=_manifest()).load(path)

    def test_duplicate_case_ids_raise(self, tmp_path) -> None:
        text = """\
# 1. Test

```yaml
kind: expectation
case_id: dup
document_alias: doc_a
entity_type: manufacturer
scope_type: whole_document
expected_fields:
  name: A
```

```yaml
kind: expectation
case_id: dup
document_alias: doc_a
entity_type: supplier
scope_type: whole_document
expected_fields:
  name: B
```
"""
        path = _write(tmp_path, text)
        with pytest.raises(SchemaValidationError):
            ExtractionExpectationLoader(manifest=_manifest()).load(path)

    def test_default_review_status_and_completeness(self, tmp_path) -> None:
        text = """\
# 1. Test

```yaml
kind: expectation
case_id: e1
document_alias: doc_a
entity_type: manufacturer
scope_type: whole_document
expected_fields:
  name: Acme
```
"""
        path = _write(tmp_path, text)
        case = ExtractionExpectationLoader(manifest=_manifest()).load(path).expectations[0]
        assert case.review_status.value == "candidate"
        assert case.completeness.value == "presence_only"

    def test_expected_evidence_parsed(self, tmp_path) -> None:
        text = """\
# 1. Test

```yaml
kind: expectation
case_id: e1
document_alias: doc_a
entity_type: safety_warning
scope_type: page_range
page_start: 9
page_end: 9
expected_fields:
  message: Biohazard
expected_evidence:
  page_start: 9
  page_end: 9
  section_heading: Maintenance Safety
```
"""
        path = _write(tmp_path, text)
        case = ExtractionExpectationLoader(manifest=_manifest()).load(path).expectations[0]
        assert case.expected_evidence is not None
        assert case.expected_evidence.section_heading == "Maintenance Safety"
