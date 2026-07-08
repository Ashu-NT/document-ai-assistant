from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


class OCRTemporaryArtifactCleaner:
    def __init__(self, root_output_dir: Path) -> None:
        self.root_output_dir = root_output_dir.resolve(strict=False)

    def cleanup(self, paths: Iterable[str | Path]) -> None:
        directories_to_prune: set[Path] = set()

        for value in paths:
            candidate = Path(value).resolve(strict=False)
            if not self._is_within_root(candidate):
                continue
            if candidate.exists() and candidate.is_file():
                try:
                    candidate.unlink()
                except OSError:
                    continue
            directories_to_prune.add(candidate.parent)

        for directory in sorted(
            directories_to_prune,
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            self._prune_empty_directories(directory)

    def _prune_empty_directories(self, directory: Path) -> None:
        current = directory.resolve(strict=False)
        while self._is_within_root(current) and current != self.root_output_dir:
            try:
                current.rmdir()
            except OSError:
                return
            current = current.parent

    def _is_within_root(self, candidate: Path) -> bool:
        try:
            candidate.relative_to(self.root_output_dir)
        except ValueError:
            return False
        return True
