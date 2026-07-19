from __future__ import annotations

"""
Diagnostic scan for mojibake (UTF-8-as-cp1252 double-decoding) artifacts in
this repo's own Python source files -- catches bugs like a literal garbled
em-dash once shipped in a user-facing string instead of a real "—"
character (see finding F1, outputs/architecture/answering_and_prompt_fresh_audit.md).

Usage:
    python -m scripts.check_source_mojibake
    python -m scripts.check_source_mojibake --json
"""

import argparse
import json
import sys
from pathlib import Path

from src.shared.text.mojibake_detector import (
    MojibakeMatch,
    iter_python_files,
    scan_paths_for_mojibake,
)

_SCAN_ROOTS = ("src", "scripts")
_EXCLUDED_FILENAMES = frozenset({"mojibake_detector.py"})


def _files_to_scan(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for root_name in _SCAN_ROOTS:
        files.extend(iter_python_files(repo_root / root_name))
    return [f for f in files if f.name not in _EXCLUDED_FILENAMES]


def _print_text(matches: list[MojibakeMatch], repo_root: Path, scanned_count: int) -> None:
    if not matches:
        print(f"No mojibake artifacts found across {scanned_count} scanned files.")
        return
    for match in matches:
        relative_path = match.file_path.relative_to(repo_root)
        print(f"{relative_path}:{match.line_number}: {match.line_text.strip()}")


def _print_json(matches: list[MojibakeMatch], repo_root: Path) -> None:
    payload = [
        {
            "file": str(match.file_path.relative_to(repo_root)),
            "line": match.line_number,
            "text": match.line_text,
        }
        for match in matches
    ]
    print(json.dumps(payload, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Machine-readable output.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    files = _files_to_scan(repo_root)
    matches = scan_paths_for_mojibake(files)

    if args.json:
        _print_json(matches, repo_root)
    else:
        _print_text(matches, repo_root, len(files))

    return 1 if matches else 0


if __name__ == "__main__":
    sys.exit(main())
