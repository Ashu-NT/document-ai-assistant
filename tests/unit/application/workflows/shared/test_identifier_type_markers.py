from src.application.services.answer_generation.formatting.identifier_answer_renderer import (
    IdentifierAnswerRenderer,
)
from src.application.workflows.retrieval.structured.structured_identifier_query_analyzer import (
    StructuredIdentifierQueryAnalyzer,
)
from src.application.workflows.shared.identifier_type_markers import (
    IDENTIFIER_TYPE_MARKERS,
)
from src.domain.common import IdentifierType


def test_part_no_and_serial_no_short_forms_are_recognized() -> None:
    """Regression test: StructuredIdentifierQueryAnalyzer's own marker dict
    used to be missing the "part no"/"serial no" short-form aliases that
    IdentifierAnswerRenderer's copy had -- meaning a question like "what's
    the part no?" was recognized as identifier-scoped by the final renderer
    but not by the earlier structured-evidence resolver. Both now read from
    the same shared dict, so both recognize the short forms."""
    analyzer = StructuredIdentifierQueryAnalyzer()

    assert analyzer.requested_identifier_types("what's the part no?") == [
        IdentifierType.PART_NUMBER
    ]
    assert analyzer.requested_identifier_types("what's the serial no?") == [
        IdentifierType.SERIAL_NUMBER
    ]


def test_structured_analyzer_and_identifier_renderer_agree_on_requested_types() -> None:
    """Cross-consistency check: since both classes now read from
    IDENTIFIER_TYPE_MARKERS instead of independently-maintained copies, they
    can no longer drift apart on which phrases map to which IdentifierType."""
    analyzer = StructuredIdentifierQueryAnalyzer()
    renderer = IdentifierAnswerRenderer()

    for question in (
        "what's the part no?",
        "what's the serial no?",
        "who is the manufacturer?",
        "list the drawing number",
        "what is the certificate number?",
    ):
        analyzer_result = set(analyzer.requested_identifier_types(question))
        renderer_result = renderer._requested_identifier_types(question)
        assert analyzer_result == renderer_result, question


def test_shared_dict_covers_every_marker_bearing_identifier_type() -> None:
    assert IDENTIFIER_TYPE_MARKERS[IdentifierType.PART_NUMBER] == (
        "part number",
        "part numbers",
        "part no",
        "part",
    )
    assert "serial no" in IDENTIFIER_TYPE_MARKERS[IdentifierType.SERIAL_NUMBER]
