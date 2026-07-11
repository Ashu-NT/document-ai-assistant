import hashlib
from pathlib import Path


def compute_hashes(file_path: Path) -> tuple[str, str]:
    digest = hashlib.sha256()

    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    file_hash = digest.hexdigest()
    return file_hash, file_hash


def format_file_size(file_size_bytes: int) -> str:
    if file_size_bytes < 1024:
        return f"{file_size_bytes} B"

    suffixes = ["KB", "MB", "GB", "TB"]
    size = float(file_size_bytes)
    suffix_index = -1
    while size >= 1024 and suffix_index < len(suffixes) - 1:
        size /= 1024
        suffix_index += 1

    precision = 0 if size >= 100 else 1
    return f"{size:.{precision}f} {suffixes[max(suffix_index, 0)]}"
