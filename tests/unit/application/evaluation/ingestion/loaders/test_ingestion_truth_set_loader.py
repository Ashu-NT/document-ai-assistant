from pathlib import Path

from src.application.evaluation import IngestionTruthSetLoader
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
