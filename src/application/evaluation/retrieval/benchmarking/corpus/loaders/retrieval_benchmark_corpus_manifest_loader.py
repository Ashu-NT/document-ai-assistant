import json
from pathlib import Path

from src.application.evaluation.retrieval.benchmarking.corpus.models import (
    RetrievalBenchmarkCorpusManifest,
)
from src.shared.exceptions import SchemaValidationError


class RetrievalBenchmarkCorpusManifestLoader:
    def load(
        self,
        path: Path | str,
    ) -> RetrievalBenchmarkCorpusManifest:
        source_path = Path(path)
        if not source_path.exists():
            raise SchemaValidationError(
                "Retrieval benchmark corpus manifest file not found.",
                details={"path": str(source_path)},
            )

        try:
            payload = json.loads(source_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(
                "Retrieval benchmark corpus manifest is not valid JSON.",
                details={"path": str(source_path)},
            ) from exc

        if not isinstance(payload, dict):
            raise SchemaValidationError(
                "Retrieval benchmark corpus manifest must be a JSON object.",
                details={"path": str(source_path)},
            )

        missing_fields = [
            field_name
            for field_name in (
                "truth_set_path",
                "input_directory",
                "generated_at",
                "documents",
            )
            if field_name not in payload
        ]
        if missing_fields:
            raise SchemaValidationError(
                "Retrieval benchmark corpus manifest is missing required fields.",
                details={
                    "path": str(source_path),
                    "missing_fields": missing_fields,
                },
            )

        if not isinstance(payload["documents"], list):
            raise SchemaValidationError(
                "Retrieval benchmark corpus manifest documents field must be a list.",
                details={"path": str(source_path)},
            )

        try:
            return RetrievalBenchmarkCorpusManifest.from_dict(payload)
        except (KeyError, TypeError, ValueError) as exc:
            raise SchemaValidationError(
                "Retrieval benchmark corpus manifest contains invalid document data.",
                details={"path": str(source_path)},
            ) from exc
