from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from src.application.reporting.document_parsing.quality.quality_result_serializer import (
    QualityResultSerializer,
)
from src.config.paths import PROJECT_ROOT

if TYPE_CHECKING:
    from src.application.validation.document_quality import DocumentQualityResult

_DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "debug_parsing"


class QualityReportWriter:
    """Writes already-computed quality-check results to outputs/debug_parsing/.

    Runs no checks itself -- callers pass in the parse/chunk DocumentQualityResult
    objects they already computed via DocumentQualityGate.
    """

    def __init__(
        self,
        output_dir: Path | str | None = None,
        *,
        result_serializer: QualityResultSerializer | None = None,
    ) -> None:
        self.output_dir = Path(output_dir) if output_dir else _DEFAULT_OUTPUT_DIR
        self.result_serializer = result_serializer or QualityResultSerializer()

    def write(
        self,
        document_id: str,
        *,
        parse_result: DocumentQualityResult,
        chunk_result: DocumentQualityResult,
    ) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{document_id}_quality_report.json"
        payload = self.result_serializer.serialize(
            document_id,
            parse_result=parse_result,
            chunk_result=chunk_result,
        )
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return path
