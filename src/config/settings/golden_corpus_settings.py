from pathlib import Path

from pydantic import Field

from src.config.paths import resolve_project_path
from src.config.settings.base_settings import AppBaseSettings


class GoldenCorpusSettings(AppBaseSettings):
    """Where the (externally/local-provisioned, not git-committed) golden
    evaluation corpus lives. See outputs/architecture/
    golden_evaluation_corpus_architecture_investigation.md - the PDF corpus
    itself is never committed; only its manifest/expectation files are."""

    root_dir: str = Field(
        default="TestDoc",
        alias="GOLDEN_CORPUS_DIR",
    )

    @property
    def root_path(self) -> Path:
        return resolve_project_path(self.root_dir)
