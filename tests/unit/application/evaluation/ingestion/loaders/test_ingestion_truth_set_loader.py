from pathlib import Path

from src.application.evaluation import IngestionTruthSetLoader
from src.application.evaluation.corpus import (
    GoldenCorpusManifest,
    GoldenDocumentManifestEntry,
)
from src.domain.common import DocumentType
from src.shared.exceptions import SchemaValidationError

import pytest


_MINIMAL_STRUCTURAL_SECTION = """
# 7. Structural Expectations

```yaml
id: struct_001
document_path: "TestDoc/fixtures/sample_manual.pdf"
expected_section_count: 5
expected_top_level_section_titles:
  - "Cover"
  - "1 General"
expected_chunk_count: 12
expected_chunk_type_counts:
  general: 8
  safety_warning: 2
expected_table_count: 1
expected_picture_count: 3
expected_cross_references:
  - clue: "See Section 8"
    expected_reference_type: section_reference
    expected_target_section: "8"
  - clue: "Annex I, Section 1.2"
notes: "example case for testing"
```
"""

_SCHEMA_TEMPLATE_BLOCK = """
```yaml
id:
document_path:
```
"""


def test_loader_parses_a_structural_expectation_case(tmp_path) -> None:
    truth_set_path = tmp_path / "truth_set.md"
    truth_set_path.write_text(_MINIMAL_STRUCTURAL_SECTION, encoding="utf-8")

    cases = IngestionTruthSetLoader().load(truth_set_path)

    assert len(cases) == 1
    case = cases[0]
    assert case.case_id == "struct_001"
    assert case.document_path == Path("TestDoc/fixtures/sample_manual.pdf")
    assert case.expected_section_count == 5
    assert case.expected_top_level_section_titles == ("Cover", "1 General")
    assert case.expected_chunk_count == 12
    assert case.expected_chunk_type_counts == {"general": 8, "safety_warning": 2}
    assert case.expected_table_count == 1
    assert case.expected_picture_count == 3
    assert case.notes == "example case for testing"


def test_loader_parses_nested_cross_reference_expectations(tmp_path) -> None:
    truth_set_path = tmp_path / "truth_set.md"
    truth_set_path.write_text(_MINIMAL_STRUCTURAL_SECTION, encoding="utf-8")

    cases = IngestionTruthSetLoader().load(truth_set_path)

    cross_references = cases[0].expected_cross_references
    assert len(cross_references) == 2
    assert cross_references[0].clue == "See Section 8"
    assert cross_references[0].expected_reference_type == "section_reference"
    assert cross_references[0].expected_target_section == "8"
    # A clue with no expected_reference_type means "must not resolve
    # internally" -- the external-directive case.
    assert cross_references[1].clue == "Annex I, Section 1.2"
    assert cross_references[1].expected_reference_type is None
    assert cross_references[1].expected_target_section is None


def test_loader_skips_the_schema_template_block(tmp_path) -> None:
    truth_set_path = tmp_path / "truth_set.md"
    truth_set_path.write_text(
        _MINIMAL_STRUCTURAL_SECTION + _SCHEMA_TEMPLATE_BLOCK, encoding="utf-8"
    )

    cases = IngestionTruthSetLoader().load(truth_set_path)

    assert len(cases) == 1


def test_loader_raises_when_file_is_missing(tmp_path) -> None:
    missing_path = tmp_path / "does_not_exist.md"

    with pytest.raises(SchemaValidationError):
        IngestionTruthSetLoader().load(missing_path)


def test_loader_raises_when_no_structural_section_present(tmp_path) -> None:
    truth_set_path = tmp_path / "truth_set.md"
    truth_set_path.write_text("# 1. Something Else\n\nno cases here\n", encoding="utf-8")

    with pytest.raises(SchemaValidationError):
        IngestionTruthSetLoader().load(truth_set_path)


def test_loader_raises_when_document_path_is_missing(tmp_path) -> None:
    truth_set_path = tmp_path / "truth_set.md"
    truth_set_path.write_text(
        "# 7. Structural Expectations\n\n```yaml\nid: bad_case\n```\n",
        encoding="utf-8",
    )

    with pytest.raises(SchemaValidationError):
        IngestionTruthSetLoader().load(truth_set_path)


def test_loader_discovers_cases_regardless_of_section_number(tmp_path) -> None:
    # Regression test: a prior version of this loader hardcoded section "7"
    # and silently stopped finding any case the moment the source file's
    # section numbering changed. Discovery must be by content shape (any
    # ```yaml block with a non-empty `id:`), scanning every section, not one
    # hardcoded number.
    truth_set_path = tmp_path / "truth_set.md"
    truth_set_path.write_text(
        "# 3. Some Renumbered Heading\n\n"
        "```yaml\n"
        "id: struct_renumbered\n"
        'document_path: "TestDoc/fixtures/sample_manual.pdf"\n'
        "expected_section_count: 9\n"
        "```\n"
        "\n"
        "# 12. A Later Section\n\n"
        "```yaml\n"
        "id: struct_later_section\n"
        'document_path: "TestDoc/fixtures/other_manual.pdf"\n'
        "expected_section_count: 4\n"
        "```\n",
        encoding="utf-8",
    )

    cases = IngestionTruthSetLoader().load(truth_set_path)

    case_ids = {case.case_id for case in cases}
    assert case_ids == {"struct_renumbered", "struct_later_section"}


def test_loader_ignores_unrelated_yaml_blocks_without_an_id(tmp_path) -> None:
    truth_set_path = tmp_path / "truth_set.md"
    truth_set_path.write_text(
        "# 4. Unrelated Section\n\n"
        "```yaml\n"
        "some_other_field: value\n"
        "```\n"
        "\n"
        "# 7. Structural Expectations\n\n"
        "```yaml\n"
        "id: struct_only_real_case\n"
        'document_path: "TestDoc/fixtures/sample_manual.pdf"\n'
        "```\n",
        encoding="utf-8",
    )

    cases = IngestionTruthSetLoader().load(truth_set_path)

    assert [case.case_id for case in cases] == ["struct_only_real_case"]


def test_loader_resolves_document_alias_via_corpus_manifest(tmp_path) -> None:
    manifest = GoldenCorpusManifest(
        [
            GoldenDocumentManifestEntry(
                alias="manual_example",
                relative_path="manual_example.pdf",
                category="manual",
                expected_document_type=DocumentType.MANUAL,
            )
        ],
        root_dir=Path("/corpus/root"),
    )
    truth_set_path = tmp_path / "truth_set.md"
    truth_set_path.write_text(
        "# 7. Structural Expectations\n\n"
        "```yaml\n"
        "id: struct_alias_case\n"
        "document_alias: manual_example\n"
        "expected_section_count: 3\n"
        "```\n",
        encoding="utf-8",
    )

    cases = IngestionTruthSetLoader(manifest=manifest).load(truth_set_path)

    assert len(cases) == 1
    case = cases[0]
    assert case.document_alias == "manual_example"
    assert case.document_path == Path("/corpus/root") / "manual_example.pdf"


def test_loader_raises_for_unknown_document_alias(tmp_path) -> None:
    manifest = GoldenCorpusManifest([], root_dir=Path("/corpus/root"))
    truth_set_path = tmp_path / "truth_set.md"
    truth_set_path.write_text(
        "# 7. Structural Expectations\n\n"
        "```yaml\n"
        "id: struct_unknown_alias\n"
        "document_alias: does_not_exist\n"
        "```\n",
        encoding="utf-8",
    )

    with pytest.raises(SchemaValidationError):
        IngestionTruthSetLoader(manifest=manifest).load(truth_set_path)


def test_loader_default_glob_scans_multiple_fixture_files(tmp_path, monkeypatch) -> None:
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()
    (fixtures_dir / "structural_expectations_one.md").write_text(
        "# 7. Structural Expectations\n\n"
        "```yaml\n"
        "id: struct_one\n"
        'document_path: "one.pdf"\n'
        "```\n",
        encoding="utf-8",
    )
    (fixtures_dir / "structural_expectations_two.md").write_text(
        "# 5. Structural Expectations\n\n"
        "```yaml\n"
        "id: struct_two\n"
        'document_path: "two.pdf"\n'
        "```\n",
        encoding="utf-8",
    )

    from src.config.settings import golden_corpus_settings

    monkeypatch.setattr(golden_corpus_settings, "root_dir", str(tmp_path))

    cases = IngestionTruthSetLoader().load()

    assert {case.case_id for case in cases} == {"struct_one", "struct_two"}
