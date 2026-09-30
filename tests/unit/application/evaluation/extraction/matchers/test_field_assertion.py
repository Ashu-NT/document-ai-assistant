from src.application.evaluation.extraction.matchers.field_assertion import (
    FieldAssertionState,
    effective_identity_fields,
    has_usable_identity_assertion,
    is_asserted,
    resolve_field_assertion,
)


class TestResolveFieldAssertion:
    def test_absent_key_is_not_asserted(self) -> None:
        state, value = resolve_field_assertion({}, "name")
        assert state is FieldAssertionState.NOT_ASSERTED
        assert value is None

    def test_present_null_is_expected_null(self) -> None:
        state, value = resolve_field_assertion({"name": None}, "name")
        assert state is FieldAssertionState.EXPECTED_NULL
        assert value is None

    def test_present_value_is_expected_value(self) -> None:
        state, value = resolve_field_assertion({"name": "Acme"}, "name")
        assert state is FieldAssertionState.EXPECTED_VALUE
        assert value == "Acme"

    def test_absent_and_explicit_null_are_distinguishable(self) -> None:
        """The exact information loss the investigation identified - key
        absence and explicit null must resolve to different states, not
        collapse to the same thing."""
        absent_state, _ = resolve_field_assertion({}, "manufacturer_name")
        null_state, _ = resolve_field_assertion(
            {"manufacturer_name": None}, "manufacturer_name"
        )
        assert absent_state is not null_state
        assert absent_state is FieldAssertionState.NOT_ASSERTED
        assert null_state is FieldAssertionState.EXPECTED_NULL


class TestIsAsserted:
    def test_absent_key(self) -> None:
        assert not is_asserted({}, "name")

    def test_present_null(self) -> None:
        assert is_asserted({"name": None}, "name")

    def test_present_value(self) -> None:
        assert is_asserted({"name": "Acme"}, "name")


class TestEffectiveIdentityFields:
    def test_drops_unasserted_identity_fields(self) -> None:
        result = effective_identity_fields(
            {"name": "Marine engine-generator set", "model_number": "20V4000M53B"},
            ("name", "model_number", "serial_number", "manufacturer_name"),
        )
        assert result == ("name", "model_number")

    def test_keeps_explicitly_null_identity_field(self) -> None:
        result = effective_identity_fields(
            {"name": "Acme", "manufacturer_name": None},
            ("name", "manufacturer_name"),
        )
        assert result == ("name", "manufacturer_name")

    def test_empty_when_nothing_asserted(self) -> None:
        result = effective_identity_fields({}, ("name", "model_number"))
        assert result == ()

    def test_preserves_input_order(self) -> None:
        result = effective_identity_fields(
            {"c": "3", "a": "1"}, ("a", "b", "c")
        )
        assert result == ("a", "c")


class TestHasUsableIdentityAssertion:
    def test_true_when_one_value_asserted(self) -> None:
        assert has_usable_identity_assertion(
            {"title": "Check engine oil level"}, ("title", "interval", "component_name")
        )

    def test_false_when_nothing_asserted(self) -> None:
        assert not has_usable_identity_assertion({}, ("symptom", "component_name"))

    def test_false_when_only_null_asserted(self) -> None:
        """Explicit null alone must NOT count as usable - asserting
        emptiness is not a positive, discriminating claim."""
        assert not has_usable_identity_assertion(
            {"component_name": None}, ("symptom", "component_name")
        )

    def test_true_when_value_and_null_both_asserted(self) -> None:
        assert has_usable_identity_assertion(
            {"symptom": "Fuel temperature is too high.", "component_name": None},
            ("symptom", "component_name"),
        )

    def test_non_identity_fields_are_irrelevant(self) -> None:
        """A value asserted on a field that isn't in the identity tuple at
        all must not count as usable identity."""
        assert not has_usable_identity_assertion(
            {"cause": "Fuel temperature is too high.", "remedy": "Reduce power"},
            ("symptom", "component_name"),
        )
