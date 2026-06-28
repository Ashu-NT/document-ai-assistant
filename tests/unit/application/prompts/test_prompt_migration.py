from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_services_no_longer_contain_large_inline_prompt_strings() -> None:
    question_generation_service = _read(
        "src/application/services/question_generation/question_generation_service.py"
    )
    chunk_type_classifier = _read(
        "src/application/workflows/parsing/builders/chunking/builders/chunk_type_llm_classifier.py"
    )

    assert "You generate concise user questions from technical document excerpts." not in (
        question_generation_service
    )
    assert "You are classifying a chunk from a technical product document." not in (
        chunk_type_classifier
    )
    assert "_build_prompt(" not in question_generation_service


def test_old_prompt_builder_import_paths_are_gone() -> None:
    old_import_markers = [
        "src.application.workflows.classification.prompt_builders",
        "src.application.workflows.extraction.prompt_builders",
        "src.application.services.answer_generation.grounded_prompt_builder",
    ]

    for path in PROJECT_ROOT.rglob("*.py"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path == Path(__file__):
            continue
        contents = path.read_text(encoding="utf-8")
        for marker in old_import_markers:
            assert marker not in contents, f"Found legacy prompt import in {path}: {marker}"
