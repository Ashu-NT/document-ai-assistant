def test_citation_display_text(sample_citation) -> None:
    text = sample_citation.display_text()

    assert "pump_manual.pdf" in text
    assert "Maintenance Schedule" in text
    assert "page: 10" in text