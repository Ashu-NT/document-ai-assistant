from src.application.workflows.parsing.normalizers.docling_value_accessors import (
    clean_text,
    get_value,
)


class _Attr:
    def __init__(self, name: str) -> None:
        self.name = name


def test_get_value_returns_none_for_none_input() -> None:
    assert get_value(None, "name") is None


def test_get_value_reads_dict_key() -> None:
    assert get_value({"name": "Preface"}, "name") == "Preface"


def test_get_value_reads_missing_dict_key_as_none() -> None:
    assert get_value({"other": "value"}, "name") is None


def test_get_value_reads_object_attribute() -> None:
    assert get_value(_Attr("Preface"), "name") == "Preface"


def test_get_value_returns_none_for_missing_attribute() -> None:
    assert get_value(_Attr("Preface"), "missing") is None


def test_clean_text_returns_none_for_none_input() -> None:
    assert clean_text(None) is None


def test_clean_text_strips_whitespace() -> None:
    assert clean_text("  Preface  ") == "Preface"


def test_clean_text_returns_none_for_blank_text() -> None:
    assert clean_text("   ") is None


def test_clean_text_coerces_non_string_input() -> None:
    assert clean_text(42) == "42"
