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


class TestOmittedVsExplicitNullIdentitySemantics:
    """Tests 1-3, 6-18 from the NOT_ASSERTED-semantics task: omitted
    identity fields never constrain matching; explicit-null identity
    fields DO constrain matching; asserted values keep existing
    exact/CONTAINS semantics unchanged. Covers all 12 entity types."""

    # --- 1/2/3: core semantics, generic ---

    def test_omitted_identity_field_does_not_constrain_matching(self) -> None:
        expectation = _expectation(ExtractionEntityType.MANUFACTURER, name="Acme")
        actual = _ActualEntity(
            entity_id="m1", fields={"name": "Acme", "website": None, "country": "Germany"}
        )
        results = match_expectations_against_actuals("manufacturer", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("name",)

    def test_explicit_null_identity_field_does_constrain_matching(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.EQUIPMENT_INFO,
            scope=_SCOPE,
            expected_fields={"name": "Pump A", "manufacturer_name": None},
        )
        actual_with_manufacturer = _ActualEntity(
            entity_id="e1",
            fields={
                "name": "Pump A",
                "model_number": None,
                "serial_number": None,
                "manufacturer_name": "Acme Corp",
            },
        )
        results = match_expectations_against_actuals(
            "equipment_info", [expectation], [actual_with_manufacturer]
        )
        assert results[0].outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED
        assert "manufacturer_name" in results[0].identity_fields_used

    def test_explicit_null_identity_field_matches_actual_also_empty(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.EQUIPMENT_INFO,
            scope=_SCOPE,
            expected_fields={"name": "Pump A", "manufacturer_name": None},
        )
        actual_no_manufacturer = _ActualEntity(
            entity_id="e1",
            fields={
                "name": "Pump A",
                "model_number": None,
                "serial_number": None,
                "manufacturer_name": None,
            },
        )
        results = match_expectations_against_actuals(
            "equipment_info", [expectation], [actual_no_manufacturer]
        )
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED

    def test_asserted_value_still_uses_existing_comparison_semantics(self) -> None:
        """An asserted (non-null) identity field keeps its existing exact
        or CONTAINS mode - this change never broadens matching for
        fields that ARE asserted, only skips fields that aren't."""
        expectation = _expectation(ExtractionEntityType.MANUFACTURER, name="Acme Corp")
        wrong_wording = _ActualEntity(
            entity_id="m1", fields={"name": "Acme Corporation", "website": None, "country": None}
        )
        results = match_expectations_against_actuals(
            "manufacturer", [expectation], [wrong_wording]
        )
        assert results[0].outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED

    # --- 6: the exact MTU-cover EquipmentInfo example from the task ---

    def test_equipment_info_partial_golden_matches_actual_with_extra_identity_fields(
        self,
    ) -> None:
        """Golden asserts only model_number (name deliberately omitted here
        to isolate the omission effect from name's own exact-match
        strictness, which this task does not change) - the model's fuller,
        additionally-populated actual (extra manufacturer_name) must still
        match, since manufacturer_name was never asserted."""
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.EQUIPMENT_INFO,
            scope=_SCOPE,
            expected_fields={"model_number": "20V4000M53B"},
        )
        actual = _ActualEntity(
            entity_id="e1",
            fields={
                "name": "Marine engine-generator set with 20V4000M53B engine",
                "model_number": "20V4000M53B",
                "serial_number": None,
                "manufacturer_name": "Rolls-Royce Solutions",
            },
        )
        results = match_expectations_against_actuals("equipment_info", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("model_number",)

    def test_equipment_info_name_still_exact_match_only_this_task_does_not_change_that(
        self,
    ) -> None:
        """Per the task's explicit instruction: do not silently introduce
        fuzzy/contains matching for EquipmentInfo.name. Asserting BOTH
        name and model_number, with a fuller actual name, must still FN on
        name - this task fixes omission semantics only."""
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.EQUIPMENT_INFO,
            scope=_SCOPE,
            expected_fields={
                "name": "Marine engine-generator set",
                "model_number": "20V4000M53B",
            },
        )
        actual = _ActualEntity(
            entity_id="e1",
            fields={
                "name": "Marine engine-generator set with 20V4000M53B engine",
                "model_number": "20V4000M53B",
                "serial_number": None,
                "manufacturer_name": "Rolls-Royce Solutions",
            },
        )
        results = match_expectations_against_actuals("equipment_info", [expectation], [actual])
        # manufacturer_name is NOT_ASSERTED now (fixed), but name is still
        # asserted and still exact-match-only, so this remains a FN.
        assert results[0].outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED
        assert "name" in results[0].identity_fields_used
        assert "manufacturer_name" not in results[0].identity_fields_used

    # --- 7: ContactPoint ---

    def test_contact_point_partial_golden_matches_actual_with_extra_identity_fields(
        self,
    ) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.CONTACT_POINT,
            scope=_SCOPE,
            expected_fields={"value": "info@example.com"},
        )
        actual = _ActualEntity(
            entity_id="cp1",
            fields={
                "contact_type": "email_address",
                "value": "info@example.com",
                "label": "General",
                "owner_name": "Acme Corp",
                "owner_entity_type": "manufacturer",
            },
        )
        results = match_expectations_against_actuals("contact_point", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("value",)

    # --- 8: MaintenanceTask ---

    def test_maintenance_task_optional_identity_fields_omission(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.MAINTENANCE_TASK,
            scope=_SCOPE,
            expected_fields={"title": "Check engine oil level"},
        )
        actual = _ActualEntity(
            entity_id="t1",
            fields={
                "title": "Check engine oil level",
                "description": None,
                "interval": "1000 hours",
                "component_name": "ENGINE OPERATIONAL MONITORING",
                "equipment_id": None,
            },
        )
        results = match_expectations_against_actuals(
            "maintenance_task", [expectation], [actual]
        )
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("title",)

    # --- 9: Procedure component_name omission ---

    def test_procedure_component_name_omission(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.PROCEDURE,
            scope=_SCOPE,
            expected_fields={"title": "Additional fuel filter"},
        )
        actual = _ActualEntity(
            entity_id="p1",
            fields={
                "title": "Additional fuel filter – Replacement",
                "procedure_type": "replacement",
                "steps": "Replace left filter",
                "component_name": "Fuel Filter",
                "equipment_id": None,
            },
        )
        results = match_expectations_against_actuals("procedure", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("title",)

    # --- 10: Specification component_name omission ---

    def test_specification_component_name_omission(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.SPECIFICATION,
            scope=_SCOPE,
            expected_fields={"parameter": "Tank Capacity"},
        )
        actual = _ActualEntity(
            entity_id="s1",
            fields={
                "parameter": "Tank Capacity",
                "value": "1200",
                "unit": "L",
                "component_name": "Tank",
            },
        )
        results = match_expectations_against_actuals("specification", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("parameter",)

    # --- 11: MaintenanceInterval component_name omission ---

    def test_maintenance_interval_component_name_omission(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.MAINTENANCE_INTERVAL,
            scope=_SCOPE,
            expected_fields={"interval": "1000 operating hours"},
        )
        actual = _ActualEntity(
            entity_id="mi1",
            fields={
                "interval": "1000 operating hours",
                "component_name": "Valve gear",
                "maintenance_task_id": None,
            },
        )
        results = match_expectations_against_actuals(
            "maintenance_interval", [expectation], [actual]
        )
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("interval",)

    # --- 12: TroubleshootingEntry component_name omission ---

    def test_troubleshooting_entry_component_name_omission(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.TROUBLESHOOTING_ENTRY,
            scope=_SCOPE,
            expected_fields={"symptom": "Fuel temperature is too high."},
        )
        actual = _ActualEntity(
            entity_id="te1",
            fields={
                "symptom": "Fuel temperature is too high.",
                "cause": None,
                "remedy": "Reduce power",
                "component_name": "Fuel System",
                "equipment_id": None,
            },
        )
        results = match_expectations_against_actuals(
            "troubleshooting_entry", [expectation], [actual]
        )
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("symptom",)

    # --- 13: SparePart optional identity fields ---

    def test_spare_part_optional_identity_fields_omission(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.SPARE_PART,
            scope=_SCOPE,
            expected_fields={"part_number": "F30379104"},
        )
        actual = _ActualEntity(
            entity_id="sp1",
            fields={
                "part_number": "F30379104",
                "description": "Oil filter wrench",
                "quantity": "1",
                "component_name": "Fuel Filter",
                "manufacturer_name": "Acme",
            },
        )
        results = match_expectations_against_actuals("spare_part", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("part_number",)

    # --- 14: Manufacturer / Supplier simple identity unchanged ---

    def test_manufacturer_simple_identity_unchanged(self) -> None:
        expectation = _expectation(ExtractionEntityType.MANUFACTURER, name="MTU Friedrichshafen GmbH")
        actual = _ActualEntity(
            entity_id="m1",
            fields={"name": "MTU Friedrichshafen GmbH", "website": None, "country": "Germany"},
        )
        results = match_expectations_against_actuals("manufacturer", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED

    def test_supplier_simple_identity_unchanged(self) -> None:
        expectation = _expectation(ExtractionEntityType.SUPPLIER, name="Acme Supply Co")
        actual = _ActualEntity(
            entity_id="s1",
            fields={"name": "Acme Supply Co", "website": "acme.example", "country": None},
        )
        results = match_expectations_against_actuals("supplier", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED

    # --- 15: SafetyWarning unchanged ---

    def test_safety_warning_behavior_unchanged(self) -> None:
        expectation = _expectation(ExtractionEntityType.SAFETY_WARNING, message="Biohazard")
        actual = _ActualEntity(
            entity_id="w1",
            fields={"warning_type": "warning", "message": "WARNING: Biohazard.", "component_name": None},
        )
        results = match_expectations_against_actuals("safety_warning", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert results[0].identity_fields_used == ("message",)

    # --- 16: ExtractedIdentifier unchanged ---

    def test_extracted_identifier_behavior_unchanged(self) -> None:
        expectation = _expectation(
            ExtractionEntityType.EXTRACTED_IDENTIFIER,
            raw_value="HAM2152268",
            identifier_type="certificate_number",
        )
        actual_match = _ActualEntity(
            entity_id="i1", fields={"raw_value": "HAM2152268", "identifier_type": "certificate_number"}
        )
        actual_wrong_type = _ActualEntity(
            entity_id="i2", fields={"raw_value": "HAM2152268", "identifier_type": "engine_serial_number"}
        )
        matched = match_expectations_against_actuals(
            "extracted_identifier", [expectation], [actual_match]
        )
        assert matched[0].outcome is ExtractionMatchOutcome.MATCHED

        unmatched = match_expectations_against_actuals(
            "extracted_identifier", [expectation], [actual_wrong_type]
        )
        assert unmatched[0].outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED

    # --- 17: ambiguous-candidate detection unchanged ---

    def test_ambiguous_candidate_detection_unchanged_with_narrower_identity(self) -> None:
        """Narrowing identity to only the asserted subset must not
        suppress ambiguity detection - if multiple actuals still equally
        match the (now possibly narrower) effective identity, this must
        still surface as ambiguous, not silently resolved."""
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.MANUFACTURER,
            scope=_SCOPE,
            expected_fields={"name": "Acme"},
        )
        actual_a = _ActualEntity(entity_id="m1", fields={"name": "Acme", "website": None, "country": "US"})
        actual_b = _ActualEntity(entity_id="m2", fields={"name": "Acme", "website": None, "country": "DE"})
        results = match_expectations_against_actuals(
            "manufacturer", [expectation], [actual_a, actual_b]
        )
        assert len(results) == 1
        assert results[0].outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED
        assert set(results[0].ambiguous_actual_entity_ids) == {"m1", "m2"}

    # --- 18: differing_fields diagnostics remain sensible ---

    def test_differing_fields_shows_not_asserted_field_populated_by_actual(self) -> None:
        """A NOT_ASSERTED identity field that the actual DID populate must
        still surface as a differing_fields diagnostic (informational),
        even though it no longer blocks the match."""
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.EQUIPMENT_INFO,
            scope=_SCOPE,
            expected_fields={"model_number": "20V4000M53B"},
        )
        actual = _ActualEntity(
            entity_id="e1",
            fields={
                "name": "Marine engine-generator set with 20V4000M53B engine",
                "model_number": "20V4000M53B",
                "serial_number": None,
                "manufacturer_name": "Rolls-Royce Solutions",
            },
        )
        results = match_expectations_against_actuals("equipment_info", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert "name" in results[0].differing_fields
        assert "manufacturer_name" in results[0].differing_fields

    def test_differing_fields_does_not_flag_explicit_null_field_that_matched(self) -> None:
        expectation = ExtractionExpectationCase(
            case_id="c1",
            document_alias="doc",
            entity_type=ExtractionEntityType.EQUIPMENT_INFO,
            scope=_SCOPE,
            expected_fields={"name": "Pump A", "manufacturer_name": None},
        )
        actual = _ActualEntity(
            entity_id="e1",
            fields={
                "name": "Pump A",
                "model_number": None,
                "serial_number": None,
                "manufacturer_name": None,
            },
        )
        results = match_expectations_against_actuals("equipment_info", [expectation], [actual])
        assert results[0].outcome is ExtractionMatchOutcome.MATCHED
        assert "manufacturer_name" not in results[0].differing_fields
