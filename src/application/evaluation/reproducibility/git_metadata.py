import subprocess
from pathlib import Path

from src.config.paths import PROJECT_ROOT


def resolve_git_commit(*, cwd: Path | None = None) -> str | None:
    """The current commit hash, or None if this isn't a Git checkout, `git`
    isn't on PATH, or the lookup otherwise fails. Never raises - git
    metadata is a reproducibility nicety, not something evaluation should
    ever fail over."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(cwd or PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if result.returncode != 0:
        return None

    commit = result.stdout.strip()
    return commit or None


__all__ = ["resolve_git_commit"]
