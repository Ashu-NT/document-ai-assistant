from __future__ import annotations

import hashlib
from pathlib import Path


def compute_file_hash(file_path: Path) -> str:
    """Compute the SHA-256 hex digest of a file's raw bytes, streamed in 1MB
    chunks so arbitrarily large source files never need to be held in memory
    at once.
    """
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
