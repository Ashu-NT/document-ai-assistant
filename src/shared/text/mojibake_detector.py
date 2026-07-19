from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# The classic UTF-8-as-cp1252/Latin-1 double-decoding artifact: a genuine
# UTF-8 multi-byte character (em/en dash, curly quotes, accented Latin
# letters, the euro sign, etc.) that gets mis-decoded one byte at a time
# and re-saved produces one of the marker sequences below -- these do not
# occur in any legitimate English/German technical-document text, so a
# substring match is a reliable, low-false-positive signal for this one
# failure mode. This is distinct from `report_text_corruption_candidates.py`,
# which targets a different defect (dropped characters) in ingested PDF
# text, not source-code string literals.
#
# This module's own marker literals necessarily contain the patterns being
# searched for -- callers must exclude this file's own path from any scan,
# or it will always report itself as a match.
_MOJIBAKE_MARKERS = ("â€", "Ã¢â‚¬", "Ã©", "Ã¨", "Ã¼", "Ã¶", "Ã¤", "Ã±")


@dataclass(slots=True, frozen=True)
class MojibakeMatch:
    file_path: Path
    line_number: int
    line_text: str


def iter_python_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(root.rglob("*.py"))


def scan_paths_for_mojibake(paths: list[Path]) -> list[MojibakeMatch]:
    matches: list[MojibakeMatch] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(marker in line for marker in _MOJIBAKE_MARKERS):
                matches.append(
                    MojibakeMatch(
                        file_path=path,
                        line_number=line_number,
                        line_text=line,
                    )
                )
    return matches
