from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_project_path(path_value: str | None) -> Path:
    if not path_value:
        return PROJECT_ROOT

    path = Path(path_value)

    if path.is_absolute():
        return path

    return PROJECT_ROOT / path


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)