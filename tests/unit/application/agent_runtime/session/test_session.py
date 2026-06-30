from src.application.agent_runtime.session import RuntimeOptions, SessionManager


def test_session_initializes() -> None:
    manager = SessionManager()

    session = manager.create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )

    assert session.session_id == "demo-session"
    assert session.selected_document.is_selected is False
    assert session.prompt_text() == "document-agent>"


def test_session_stores_selected_document_from_snapshot() -> None:
    manager = SessionManager()

    session = manager.create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
        snapshot={
            "selected_document_id": "doc_001",
            "selected_document_title": "FWC12 Manual",
            "selected_document_file_name": "FWC12 Manual.pdf",
        },
    )

    assert session.selected_document.document_id == "doc_001"
    assert session.selected_document.display_name == "FWC12 Manual"


def test_prompt_shows_selected_document() -> None:
    manager = SessionManager()

    session = manager.create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
        snapshot={
            "selected_document_id": "doc_001",
            "selected_document_title": "FWC12 Manual",
        },
    )

    assert session.prompt_text() == "document-agent [FWC12]>"
