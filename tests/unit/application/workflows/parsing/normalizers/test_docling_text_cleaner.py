from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)


def test_repair_docling_text_fixes_common_cp1252_utf8_mojibake() -> None:
    apostrophe_mojibake = b"Don\xe2\x80\x99ts".decode("cp1252")
    quote_mojibake = b"G1/2\xe2\x80\x9d".decode("latin1")

    assert repair_docling_text(apostrophe_mojibake) == "Don\u2019ts"
    assert repair_docling_text(quote_mojibake) == "G1/2\u201d"


def test_repair_docling_text_fixes_common_symbol_mojibake() -> None:
    symbol_mojibake = b"\xe2\x80\xa2 Navigate \xe2\x86\x92 Setup \xe2\x89\xa4 80 \xc2\xb0C".decode(
        "cp1252"
    )

    assert repair_docling_text(symbol_mojibake) == "\u2022 Navigate \u2192 Setup \u2264 80 \u00b0C"


def test_repair_docling_text_preserves_clean_unicode_text() -> None:
    assert repair_docling_text("Maintenance Intervals") == "Maintenance Intervals"
    assert repair_docling_text("P&ID Pos Nr.") == "P&ID Pos Nr."
