from src.application.workflows.parsing.tables.semantics.table_semantic_rule_evaluator import (
    TableSemanticRuleEvaluator,
)


def _evaluator() -> TableSemanticRuleEvaluator:
    return TableSemanticRuleEvaluator()


def test_detects_cycles_column_as_a_frequency_synonym() -> None:

    evaluator = _evaluator()
    headers = ["description", "cycles"]
    direct_text = (
        "description cycles functional test monthly "
        "maintenance with more than 500 opening closing cycles per year yearly half yearly "
        "exchange batteries of radio control yearly "
        "exchange batteries of control unit every 2 years"
    )
    assert evaluator.looks_like_maintenance_interval_table(headers, [], direct_text)


def test_detects_regular_intermittent_frequency_adjectives() -> None:

    evaluator = _evaluator()
    headers = ["description", "regular", "intermittent"]
    direct_text = (
        "description regular intermittent "
        "feed water solenoid valve does not require regular maintenance check for leaks "
        "cartridge filters change cartridges when pressure after the filter drops down to 3.5 psi or every 3 months "
        "low pressure switch test once every 6 months check for leaks "
        "hp pump every 8000 hrs when leaking check for leaks check for motor bearing noise "
        "cleaning pump requires very little maintenance change shaft seal every 2 000 hours"
    )
    assert evaluator.looks_like_maintenance_interval_table(headers, [], direct_text)


def test_detects_interval_word_in_a_collapsed_multi_word_header_cell() -> None:

    evaluator = _evaluator()
    headers = ["", "", "task interval done comments"]
    direct_text = (
        "task interval done comments check electrical connections annual "
        "check if all functions are working monthly clean all components monthly"
    )
    assert evaluator.looks_like_maintenance_interval_table(headers, [], direct_text)


def test_detects_single_column_narrative_maintenance_list() -> None:
    # Real document: no columns/header at all -- one full sentence per
    # row, each embedding its own interval ("Every 5 years: replace...").
    evaluator = _evaluator()
    headers = []
    direct_text = (
        "scheduled every 5 years change lubricating oil "
        "every 5 years replace bearing components on the covers "
        "every 10 years replace the sealing lips "
        "condition based check underwater components and replace if necessary"
    )
    assert evaluator.looks_like_maintenance_interval_table(headers, [], direct_text)


def test_detects_interval_signal_from_a_stack_of_frequency_named_section_headings() -> None:

    evaluator = _evaluator()
    headers = ["action", "imo msc.1-circ.1432 & msc.1-circ.1516", "marioff recommendations"]
    direct_text = (
        "action imo msc 1 circ 1432 msc 1 circ 1516 marioff recommendations "
        "assess system water quality in the header tank and pump unit "
        "update the service records"
    )
    section_text = (
        "weekly testing and inspections monthly testing and inspections "
        "quarterly testing and inspections annual testing inspections and service "
        "two year testing inspections and service five year testing inspections and service"
    )
    assert evaluator.looks_like_maintenance_interval_table(
        headers, [], direct_text, section_text
    )


def test_does_not_treat_a_single_temporal_section_heading_as_interval_signal() -> None:
    # The section-path fallback requires 3+ DISTINCT temporal words, not
    # just one -- a table under an ordinary "Annual Inspection" section
    # heading with no other interval vocabulary must not be swept in.
    evaluator = _evaluator()
    headers = ["parameter", "value"]
    direct_text = "parameter value voltage 400v power 5.5 kw weight 120 kg"
    section_text = "annual inspection"
    assert not evaluator.looks_like_maintenance_interval_table(
        headers, [], direct_text, section_text
    )


def test_does_not_steal_a_troubleshooting_table() -> None:

    evaluator = _evaluator()
    headers = ["symptom", "cause", "remedy"]
    direct_text = (
        "symptom cause remedy pump does not start check the power supply and replace the fuse if blown "
        "no discharge check the strainer clean if blocked and replace the impeller if worn "
        "annual inspection recommended"
    )
    assert not evaluator.looks_like_maintenance_interval_table(headers, [], direct_text)


def test_does_not_steal_a_toc_table() -> None:

    evaluator = _evaluator()
    headers = ["number", "title", "page"]
    direct_text = (
        "number title page 5 maintenance schedule 45 6 annual inspection checklist 52"
    )
    assert not evaluator.looks_like_maintenance_interval_table(headers, [], direct_text)


def test_does_not_treat_an_ambiguous_body_mention_of_frequency_as_interval_vocabulary() -> None:

    evaluator = _evaluator()
    headers = ["symptom", "cause", "remedy"]
    direct_text = (
        "symptom cause remedy the engine does not start "
        "unsuitable power supply incorrect electrical connections "
        "check that the mains frequency and voltage correspond to the electrical characteristics "
        "replace the fuses check the power supply"
    )
    assert not evaluator.looks_like_maintenance_interval_table(headers, [], direct_text)


def test_detects_incident_solution_header_as_troubleshooting_synonyms() -> None:

    evaluator = _evaluator()
    headers = ["incident", "cause", "solution"]
    direct_text = (
        "incident cause solution softener fails to regenerate interrupted power "
        "defective power head restore electrics mains fuse change power head"
    )
    assert evaluator.looks_like_troubleshooting_table(headers, direct_text, "")


def test_detects_alarm_details_possible_cause_what_to_do_header() -> None:

    evaluator = _evaluator()
    headers = ["alarm details", "possible cause", "what to do?"]
    direct_text = (
        "alarm details possible cause what to do process flow too low "
        "flow is too low increase flow check pressure and flow from ballast pump"
    )
    assert evaluator.looks_like_troubleshooting_table(headers, direct_text, "")


def test_does_not_flag_an_unrelated_specification_table() -> None:
    evaluator = _evaluator()
    headers = ["parameter", "value"]
    direct_text = "parameter value voltage 400v power 5.5 kw weight 120 kg"
    assert not evaluator.looks_like_maintenance_interval_table(headers, [], direct_text)
