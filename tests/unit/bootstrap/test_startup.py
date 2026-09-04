from src.bootstrap import startup


def test_bootstrap_application_configures_logging(monkeypatch) -> None:
    """Regression: configure_logging() existed but was never called from
    anywhere, so no ingestion-stage log line was ever actually emitted
    (only Python's stderr handler-of-last-resort). This is what makes the
    stage logging added throughout ingestion actually visible."""
    calls: list[bool] = []
    monkeypatch.setattr(startup, "configure_logging", lambda: calls.append(True))

    startup.bootstrap_application()

    assert calls == [True]
