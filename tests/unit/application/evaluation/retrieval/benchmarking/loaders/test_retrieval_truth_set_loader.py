from collections import Counter
from pathlib import Path
from uuid import uuid4

import pytest

from src.application.evaluation import (
    DEFAULT_RETRIEVAL_TRUTH_SET_PATH,
    RetrievalBenchmarkPriority,
    RetrievalBenchmarkQueryType,
    RetrievalBenchmarkRankTarget,
    RetrievalTruthSetLoader,
)
from src.shared.exceptions import SchemaValidationError


def test_loader_uses_default_truth_set_path() -> None:
    dataset = RetrievalTruthSetLoader().load()

    assert dataset.source_path == DEFAULT_RETRIEVAL_TRUTH_SET_PATH
    assert dataset.case_count == 122


def test_loader_accepts_custom_path_override() -> None:
    truth_set_path = _write_workspace_temp_file(
        "custom_truth_set",
        _truth_set_with_single_case(),
    )

    try:
        dataset = RetrievalTruthSetLoader().load(truth_set_path)

        assert dataset.source_path == truth_set_path
        assert [case.case_id for case in dataset.cases] == ["X-001"]
    finally:
        truth_set_path.unlink(missing_ok=True)


def test_loader_parses_all_canonical_cases_and_ignores_schema_example() -> None:
    dataset = RetrievalTruthSetLoader().load()

    assert dataset.case_count == 122
    assert dataset.cases[0].case_id == "M-001"
    assert all(case.case_id for case in dataset.cases)


def test_loader_matches_document_family_counts() -> None:
    dataset = RetrievalTruthSetLoader().load()

    family_counts = Counter(
        case.expected_document_alias.split("_", 1)[0]
        for case in dataset.cases
        if case.expected_document_alias is not None
    )

    assert family_counts == {
        "manual": 33,      # 22 (fwc12) + 4 (puro30) + 4 (bauer_mv320) + 3 (softener_9500)
        "certificate": 29,  # 8 (hoses) + 3 (ehlers) + 3 (ac_generators) + 3 (motor_k2200110) + 3 (rolls_royce) + 3 (mtu) + 3 (ship_sanitation) + 3 (gea)
        "drawing": 11,     # 8 (nav_lights) + 3 (ship_name_aft)
        "datasheet": 22,   # 10 (mk311xxx) + 3 (motor_p62b355l4) + 3 (deck_fillers) + 3 (rule_bilge_pumps) + 3 (volvo_penta_d6_440)
        "report": 27,      # 18 (pressure_transmitter) + 3 (transformer_d4000240) + 3 (man_shop_test) + 3 (vedder_maintenance)
    }


def test_loader_normalizes_enum_values_from_markdown() -> None:
    truth_set_path = _write_workspace_temp_file(
        "normalized_truth_set",
        _truth_set_with_single_case(
            query_type="Procedure Lookup",
            priority="High",
            expected_rank="Top-3",
        ),
    )

    try:
        dataset = RetrievalTruthSetLoader().load(truth_set_path)
        case = dataset.cases[0]

        assert case.query_type == RetrievalBenchmarkQueryType.PROCEDURE_LOOKUP
        assert case.priority == RetrievalBenchmarkPriority.HIGH
        assert case.expected_rank_target == RetrievalBenchmarkRankTarget.TOP_3
    finally:
        truth_set_path.unlink(missing_ok=True)


def test_loader_exposes_subset_definitions_and_filtered_case_views() -> None:
    dataset = RetrievalTruthSetLoader().load()

    assert dataset.identifier_subset_definition is not None
    assert dataset.semantic_procedure_subset_definition is not None
    assert dataset.identifier_subset_definition.row_count == 15
    assert dataset.semantic_procedure_subset_definition.row_count == 10
    assert any(case.case_id == "C-001" for case in dataset.identifier_focused_cases)
    assert any(case.case_id == "M-008" for case in dataset.semantic_procedure_cases)


def test_loader_raises_for_malformed_yaml_block() -> None:
    truth_set_path = _write_workspace_temp_file(
        "malformed_truth_set",
        _truth_set_with_raw_case_block(
            "\n".join(
                [
                    "id: X-001",
                    "query this line is malformed",
                    "query_type: identifier_lookup",
                    "expected_document_id: sample_doc",
                    "expected_file: sample.pdf",
                    "expected_section_path: Cover",
                    "expected_page: 1",
                    'expected_relevant_passage: "Sample passage."',
                    "priority: high",
                    "expected_rank: top_1",
                ]
            )
        ),
    )

    try:
        with pytest.raises(SchemaValidationError):
            RetrievalTruthSetLoader().load(truth_set_path)
    finally:
        truth_set_path.unlink(missing_ok=True)


def test_loader_raises_for_missing_required_case_fields() -> None:
    truth_set_path = _write_workspace_temp_file(
        "missing_field_truth_set",
        _truth_set_with_raw_case_block(
            "\n".join(
                [
                    "id: X-001",
                    'query: "What is the sample?"',
                    "query_type: identifier_lookup",
                    "expected_document_id: sample_doc",
                    "expected_file: sample.pdf",
                    "expected_section_path: Cover",
                    "expected_page: 1",
                    'expected_relevant_passage: "Sample passage."',
                    "priority: high",
                ]
            )
        ),
    )

    try:
        with pytest.raises(SchemaValidationError):
            RetrievalTruthSetLoader().load(truth_set_path)
    finally:
        truth_set_path.unlink(missing_ok=True)


def _truth_set_with_single_case(
    *,
    query_type: str = "identifier_lookup",
    priority: str = "high",
    expected_rank: str = "top_1",
) -> str:
    return _truth_set_with_raw_case_block(
        "\n".join(
            [
                "id: X-001",
                'query: "What is the sample identifier?"',
                f"query_type: {query_type}",
                "expected_document_id: sample_doc",
                'expected_file: "sample.pdf"',
                'expected_section_path: "Title / Cover"',
                "expected_page: 1",
                'expected_relevant_passage: "Sample identifier ABC-123."',
                f"priority: {priority}",
                f"expected_rank: {expected_rank}",
                'notes: "Sample note."',
            ]
        )
    )


def _truth_set_with_raw_case_block(case_block: str) -> str:
    return "\n".join(
        [
            "# Retrieval Evaluation Truth Set",
            "",
            "## 1. Corpus Inventory",
            "",
            "# 4. Truth Set",
            "",
            "## 4.1 Sample",
            "",
            "```yaml",
            case_block,
            "```",
            "",
            "# 5. Identifier-Heavy Evaluation Subset",
            "",
            "| ID | Identifier | Expected File | Expected Evidence |",
            "|---|---|---|---|",
            "| `ID-001` | `ABC-123` | Sample | Cover identifier. |",
            "",
            "# 6. Semantic / Procedure Evaluation Subset",
            "",
            "| ID | Question | Expected Area |",
            "|---|---|---|",
            '| `SEM-001` | "How do I use the sample?" | Sample > Procedure |',
        ]
    )


def _write_workspace_temp_file(
    stem: str,
    content: str,
) -> Path:
    base_path = Path("outputs/test_retrieval_truth_set_loader")
    base_path.mkdir(parents=True, exist_ok=True)
    file_path = base_path / f"{stem}_{uuid4().hex}.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path
