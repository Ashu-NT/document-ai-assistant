from src.application.langgraph.reflection.detectors.spare_parts_list_context_detector import (
    is_legitimate_partial_spare_parts_answer,
)

_BARE_PARTIAL_NOTICE_NO_DATA = (
    "This is only a partial list of spare parts (see page 4); specific part "
    "numbers could not be extracted."
)

_GENUINE_PARTIAL_WITH_ROW_DATA = (
    "Spare parts lists found:\n\n"
    "1. Spare Parts List\n"
    "   Pages: 85-87\n\n"
    "   Available rows:\n"
    "   - Description: Filter\n"
    "     Part No.: A00103\n\n"
    "Only a partial list of spare parts could be extracted from the "
    "retrieved context.\n"
)


def test_bare_partial_notice_with_no_actual_row_data_is_not_legitimate() -> None:
    """Reproduces the exact investigation misfire (finding 4.4a): the bare
    word 'partial' plus 'page', with no identifying/raw row data, must no
    longer be accepted as legitimate partial coverage."""
    assert is_legitimate_partial_spare_parts_answer(_BARE_PARTIAL_NOTICE_NO_DATA) is False


def test_genuine_partial_notice_with_real_row_data_still_legitimate() -> None:
    assert is_legitimate_partial_spare_parts_answer(_GENUINE_PARTIAL_WITH_ROW_DATA) is True


def test_raw_row_alone_without_partial_notice_is_still_legitimate() -> None:
    answer = (
        "Spare parts list found on page 12.\n"
        "Raw Row: 4 | Filter Cartridge | A00220\n"
    )
    assert is_legitimate_partial_spare_parts_answer(answer) is True


def test_no_spare_parts_marker_at_all_is_not_legitimate() -> None:
    assert is_legitimate_partial_spare_parts_answer("This document has no relevant data.") is False
