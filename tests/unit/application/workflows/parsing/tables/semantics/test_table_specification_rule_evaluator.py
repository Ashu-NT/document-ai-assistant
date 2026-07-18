from src.application.workflows.parsing.tables.semantics.table_specification_rule_evaluator import (
    TableSpecificationRuleEvaluator,
)


def _evaluator() -> TableSpecificationRuleEvaluator:
    return TableSpecificationRuleEvaluator()


def test_technical_data_table_ignores_the_canonicalizer_synthetic_label_value_header() -> None:

    evaluator = _evaluator()
    headers = ["label", "value"]
    labels = [
        "function of buttons is disabled in the settings",
        "damaged processor",
        "blackout",
    ]
    direct_text = (
        "label value function of buttons is disabled in the settings "
        "set button up and button down to j in control unit damaged processor "
        "replace processor blackout restore main power supply"
    )
    assert not evaluator.looks_like_technical_data_table(headers, labels, direct_text, "")


def test_technical_data_table_still_detects_a_genuine_parameter_value_header() -> None:
    # A REAL author-written "Parameter"/"Value" header (not the
    # canonicalizer's synthetic "Label"/"Value" placeholder) must still be
    # recognized.
    evaluator = _evaluator()
    headers = ["parameter", "value"]
    labels = ["supply voltage", "rated power", "operating temperature"]
    direct_text = (
        "parameter value supply voltage 400v rated power 5.5 kw "
        "operating temperature -10 to 60 c"
    )
    assert evaluator.looks_like_technical_data_table(headers, labels, direct_text, "")


def test_technical_data_table_still_detects_via_label_hits_without_explicit_header() -> None:
    evaluator = _evaluator()
    headers = ["label", "value"]
    labels = ["supply voltage", "rated power"]
    direct_text = (
        "label value supply voltage 400v rated power 5.5 kw weight 120 kg"
    )
    assert evaluator.looks_like_technical_data_table(headers, labels, direct_text, "")
