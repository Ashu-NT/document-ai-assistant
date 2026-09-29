from __future__ import annotations

"""
Phase 2A classification golden evaluation, run for real: real golden corpus
documents (via the Parsed Artifact Store - cached where already warmed, real
Docling otherwise), a real Ollama LLM classification call per document in
FRESH_MODEL mode (`DocumentClassificationWorkflow.classify_document_attempt()`
- never the cached/reclassification-gated `classify_document()` path).

Deliberately marked `slow` and `e2e`, same convention as
test_answer_quality_regression_gate.py - never picked up by the fast
`tests/unit/` suite, requires a locally reachable Ollama instance and the
golden corpus provisioned under TestDoc/ (externally/local-provisioned,
never committed).

Usage:
    $env:RUN_LIVE_CLASSIFICATION_GOLDEN_EVAL="true"
    pytest -m slow tests/e2e/test_classification_golden_evaluation.py
"""

import os

import pytest

from src.application.evaluation.classification import run_classification_golden_evaluation
from src.application.evaluation.corpus import GoldenCorpusManifest, GoldenDocumentAvailability
from src.application.reporting.golden_evaluation import GoldenEvaluationReportWriter
from src.config.paths import PROJECT_ROOT

_RUN_LIVE_CLASSIFICATION_GOLDEN_EVAL = (
    os.getenv("RUN_LIVE_CLASSIFICATION_GOLDEN_EVAL", "").strip().lower()
    in {"1", "true", "yes", "on"}
)

pytestmark = [
    pytest.mark.slow,
    pytest.mark.e2e,
    pytest.mark.skipif(
        not _RUN_LIVE_CLASSIFICATION_GOLDEN_EVAL,
        reason=(
            "requires the golden corpus provisioned under TestDoc/ and a live "
            "Ollama runtime; set RUN_LIVE_CLASSIFICATION_GOLDEN_EVAL=true to run"
        ),
    ),
]


def test_classification_golden_evaluation_against_available_corpus() -> None:
    manifest = GoldenCorpusManifest.default()
    resolved_documents = manifest.resolve_all()
    available = [
        r for r in resolved_documents if r.availability == GoldenDocumentAvailability.AVAILABLE
    ]

    if not available:
        pytest.skip(
            "Golden corpus not provisioned locally under TestDoc/ - skipping "
            "classification golden evaluation."
        )

    report = run_classification_golden_evaluation(manifest=manifest, allow_real_parsing=True)

    writer = GoldenEvaluationReportWriter()
    output_dir = PROJECT_ROOT / "outputs" / "evaluation" / "golden"
    writer.write_json(report, output_dir / "golden_evaluation_report.json")
    writer.write_markdown(report, output_dir / "golden_evaluation_report.md")

    # Every AVAILABLE document must have actually been classified (or have
    # an explicit, visible EXECUTION_FAILED/SKIPPED reason) - never silently
    # missing from the classification_results list.
    aliases_with_results = {r.alias for r in report.classification_results}
    missing = {r.alias for r in available} - aliases_with_results
    assert not missing, f"Available golden documents produced no classification outcome at all: {missing}"

    execution_failures = [
        r for r in report.classification_results if r.execution_error is not None
    ]
    assert not execution_failures, (
        "Classification execution failures in the golden corpus: "
        f"{[(r.alias, r.execution_error) for r in execution_failures]}"
    )
