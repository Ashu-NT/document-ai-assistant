from src.application.evaluation.extraction.extraction_completeness import (
    ExtractionCompleteness,
)
from src.application.evaluation.extraction.extraction_entity_type import (
    ExtractionEntityType,
)
from src.application.evaluation.extraction.extraction_evaluation_scope import (
    ExtractionEvaluationScope,
)
from src.application.evaluation.extraction.extraction_expectation_case import (
    ExtractionExpectationCase,
)
from src.application.evaluation.extraction.extraction_review_status import (
    ExtractionReviewStatus,
)
from src.application.evaluation.extraction.matchers.extraction_entity_matcher import (
    _ActualEntity,
    match_expectations_against_actuals,
)
from src.application.evaluation.extraction.matchers.extraction_match_result import (
    ExtractionMatchOutcome,
)

_SCOPE = ExtractionEvaluationScope.whole_document()


def _expectation(entity_type: ExtractionEntityType, **fields: str) -> ExtractionExpectationCase:
    return ExtractionExpectationCase(
        case_id=f"case_{entity_type.value}",
        document_alias="doc",
        entity_type=entity_type,
        scope=_SCOPE,
        expected_fields=fields,
    )


class TestExactIdentityMatch:
    def test_manufacturer_exact_name_match(self) -> None:
        expectation = _expectation(ExtractionEntityType.MANUFACTURER, name="Acme Corp")
        actual = _ActualEntity(entity_id="m1", fields={"name": "Acme Corp", "website": None, "country": None})

        results = match_expectations_against_actuals(
            "manufacturer", [expectation], [actual]
        )

        assert len(results) == 1
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].actual_entity_id == "m1"

    def test_manufacturer_case_and_whitespace_insensitive(self) -> None:
        expectation = _expectation(ExtractionEntityType.MANUFACTURER, name="  Acme Corp  ")
        actual = _ActualEntity(entity_id="m1", fields={"name": "acme corp", "website": None, "country": None})

        results = match_expectations_against_actuals(
            "manufacturer", [expectation], [actual]
        )

        assert results[0].outcome is ExtractionMatchOutcome.MATCHED

    def test_manufacturer_wording_mismatch_is_unmatched_expected(self) -> None:
        expectation = _expectation(ExtractionEntityType.MANUFACTURER, name="Acme Corp")
        actual = _ActualEntity(entity_id="m1", fields={"name": "Acme Corporation", "website": None, "country": None})

        results = match_expectations_against_actuals(
            "manufacturer", [expectation], [actual]
        )

        assert results[0].outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED


class TestContainsFallback:
    def test_safety_warning_message_matches_via_containment(self) -> None:
        expectation = _expectation(ExtractionEntityType.SAFETY_WARNING, message="Biohazard")
        actual = _ActualEntity(
            entity_id="w1",
            fields={"warning_type": "biological", "message": "WARNING: Biohazard. Flush pipelines first.", "component_name": None},
        )

        results = match_expectations_against_actuals(
            "safety_warning", [expectation], [actual]
        )

        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].match_reason == "identity fields matched"

    def test_safety_warning_no_containment_is_unmatched(self) -> None:
        expectation = _expectation(ExtractionEntityType.SAFETY_WARNING, message="Electric shock")
        actual = _ActualEntity(
            entity_id="w1",
            fields={"warning_type": None, "message": "Biohazard risk near pumps.", "component_name": None},
        )

        results = match_expectations_against_actuals(
            "safety_warning", [expectation], [actual]
        )

        assert results[0].outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED


class TestDuplicateAndAmbiguousCandidates:
    def test_ambiguous_when_multiple_actuals_share_identity(self) -> None:
        expectation = _expectation(
            ExtractionEntityType.TROUBLESHOOTING_ENTRY, symptom="", component_name=""
        )
        actual_a = _ActualEntity(entity_id="t1", fields={"symptom": None, "cause": "A", "remedy": "X", "component_name": None, "equipment_id": None})
        actual_b = _ActualEntity(entity_id="t2", fields={"symptom": None, "cause": "B", "remedy": "Y", "component_name": None, "equipment_id": None})

        results = match_expectations_against_actuals(
            "troubleshooting_entry", [expectation], [actual_a, actual_b]
        )

        assert len(results) == 1
        assert results[0].outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED
        assert set(results[0].ambiguous_actual_entity_ids) == {"t1", "t2"}
        assert "ambiguous" in results[0].match_reason

    def test_deterministic_ordering_not_silently_resolved(self) -> None:
        """Running the same ambiguous input twice must give the same
        (still-ambiguous) result - never an unstable pick."""
        expectation = _expectation(ExtractionEntityType.SUPPLIER, name="")
        actuals = [
            _ActualEntity(entity_id="s1", fields={"name": None, "website": None, "country": None}),
            _ActualEntity(entity_id="s2", fields={"name": None, "website": None, "country": None}),
        ]

        first = match_expectations_against_actuals("supplier", [expectation], actuals)
        second = match_expectations_against_actuals("supplier", [expectation], actuals)

        assert first[0].ambiguous_actual_entity_ids == second[0].ambiguous_actual_entity_ids


class TestUnmatchedActualsAndExhaustiveFalsePositives:
    def test_presence_only_unmatched_actual_is_reported_but_not_a_failure_signal(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.MANUFACTURER,
            scope=_SCOPE,
            completeness=ExtractionCompleteness.PRESENCE_ONLY,
            expected_fields={"name": "Acme"},
        )
        matched_actual = _ActualEntity(entity_id="m1", fields={"name": "Acme", "website": None, "country": None})
        extra_actual = _ActualEntity(entity_id="m2", fields={"name": "Unexpected Co", "website": None, "country": None})

        results = match_expectations_against_actuals(
            "manufacturer", [expectation], [matched_actual, extra_actual]
        )

        outcomes = {r.actual_entity_id: r.outcome for r in results}
        assert outcomes["m1"] is ExtractionMatchOutcome.MATCHED
        assert outcomes["m2"] is ExtractionMatchOutcome.UNMATCHED_ACTUAL
        unmatched = next(r for r in results if r.actual_entity_id == "m2")
        assert unmatched.group_completeness is ExtractionCompleteness.PRESENCE_ONLY

    def test_exhaustive_unmatched_actual_carries_exhaustive_completeness_for_fp_scoring(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.MANUFACTURER,
            scope=_SCOPE,
            completeness=ExtractionCompleteness.EXHAUSTIVE,
            expected_fields={"name": "Acme"},
        )
        matched_actual = _ActualEntity(entity_id="m1", fields={"name": "Acme", "website": None, "country": None})
        extra_actual = _ActualEntity(entity_id="m2", fields={"name": "Unexpected Co", "website": None, "country": None})

        results = match_expectations_against_actuals(
            "manufacturer", [expectation], [matched_actual, extra_actual]
        )

        unmatched = next(r for r in results if r.actual_entity_id == "m2")
        assert unmatched.outcome is ExtractionMatchOutcome.UNMATCHED_ACTUAL
        assert unmatched.group_completeness is ExtractionCompleteness.EXHAUSTIVE


class TestGroupMetadataPropagation:
    def test_group_review_status_propagates_from_expectation(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.MANUFACTURER,
            scope=_SCOPE,
            review_status=ExtractionReviewStatus.REVIEWED,
            expected_fields={"name": "Acme"},
        )
        actual = _ActualEntity(entity_id="m1", fields={"name": "Acme", "website": None, "country": None})

        results = match_expectations_against_actuals("manufacturer", [expectation], [actual])

        assert results[0].group_review_status is ExtractionReviewStatus.REVIEWED


class TestProductionIdentitySemantics:
    def test_spare_part_identity_uses_part_number_manufacturer_component(self) -> None:
        expectation = _expectation(
            ExtractionEntityType.SPARE_PART,
            part_number="F30379104",
            manufacturer_name="",
            component_name="",
        )
        # Different `description`/`quantity` must not block a match - those
        # are not identity fields for SparePart (spare_part_merger.py).
        actual = _ActualEntity(
            entity_id="p1",
            fields={
                "part_number": "F30379104",
                "description": "Oil filter wrench",
                "quantity": "1",
                "component_name": None,
                "manufacturer_name": None,
            },
        )

        results = match_expectations_against_actuals("spare_part", [expectation], [actual])

        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert "quantity" not in results[0].identity_fields_used

    def test_extracted_identifier_identity_is_raw_value_and_type(self) -> None:
        expectation = _expectation(
            ExtractionEntityType.EXTRACTED_IDENTIFIER,
            raw_value="HAM2152268",
            identifier_type="certificate_number",
        )
        actual_same_type = _ActualEntity(
            entity_id="i1", fields={"raw_value": "HAM2152268", "identifier_type": "certificate_number"}
        )
        actual_diff_type = _ActualEntity(
            entity_id="i2", fields={"raw_value": "HAM2152268", "identifier_type": "certificate"}
        )

        results = match_expectations_against_actuals(
            "extracted_identifier", [expectation], [actual_same_type]
        )
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED

        results_mismatched_type = match_expectations_against_actuals(
            "extracted_identifier", [expectation], [actual_diff_type]
        )
        assert results_mismatched_type[0].outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED


class TestIdentityFieldsOverride:
    def test_override_replaces_default_identity_fields(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.SPECIFICATION,
            scope=_SCOPE,
            expected_fields={"parameter": "Voltage", "component_name": "Pump A"},
            identity_fields_override=("parameter",),
        )
        actual = _ActualEntity(
            entity_id="s1",
            fields={"parameter": "Voltage", "value": None, "unit": None, "component_name": "Pump B"},
        )

        results = match_expectations_against_actuals("specification", [expectation], [actual])

        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("parameter",)


class TestDifferingFieldsDiagnostic:
    def test_differing_fields_reported_without_invalidating_match(self) -> None:
        expectation = _expectation(
            ExtractionEntityType.SPECIFICATION, parameter="Tank Capacity", component_name=""
        )
        actual = _ActualEntity(
            entity_id="s1",
            fields={"parameter": "Tank Capacity", "value": "1,200", "unit": "L", "component_name": None},
        )

        results = match_expectations_against_actuals("specification", [expectation], [actual])

        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert "value" in results[0].differing_fields
        assert "unit" in results[0].differing_fields
