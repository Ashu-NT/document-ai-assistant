from pathlib import Path

from src.shared.text.mojibake_detector import iter_python_files, scan_paths_for_mojibake

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCAN_ROOTS = ("src", "scripts")
_EXCLUDED_FILENAMES = frozenset({"mojibake_detector.py"})


def test_no_mojibake_artifacts_in_src_or_scripts() -> None:
    """Regression guard for finding F1
    (outputs/architecture/answering_and_prompt_fresh_audit.md): a UTF-8
    em-dash mis-decoded as cp1252/Latin-1 shipped to end users undetected
    as a garbled string. Runs on every test-suite invocation -- this
    codebase's de facto CI gate -- so this class of bug can't silently
    reappear anywhere in src/ or scripts/."""
    files = [
        file
        for root_name in _SCAN_ROOTS
        for file in iter_python_files(_REPO_ROOT / root_name)
        if file.name not in _EXCLUDED_FILENAMES
    ]

    matches = scan_paths_for_mojibake(files)

    assert not matches, "Mojibake artifacts found:\n" + "\n".join(
        f"{match.file_path}:{match.line_number}: {match.line_text.strip()}"
        for match in matches
    )
