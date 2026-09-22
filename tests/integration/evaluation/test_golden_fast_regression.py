"""Fast golden-regression tier (see outputs/architecture/
golden_evaluation_corpus_architecture_investigation.md). Requires the
golden corpus to be provisioned locally under TestDoc/ (externally/local-
provisioned, never committed - see approved decision 1); real Docling
conversion for any not-yet-cached document. Marked `integration`, never
required by the normal unit suite.

If the golden corpus is not provisioned at all in this environment, this
test SKIPS with an explicit reason rather than silently reporting success.
If part of the corpus is available, it is evaluated and asserted on; gaps
are visible in the skip/failure messages, never silently absorbed as if the
whole corpus had passed.
"""

import pytest

from src.application.evaluation.corpus import (
    GoldenCorpusManifest,
    GoldenDocumentAvailability,
)
from src.application.evaluation.golden import run_fast_golden_regression
from src.application.reporting.golden_evaluation import GoldenEvaluationReportWriter
from src.config.paths import PROJECT_ROOT

pytestmark = pytest.mark.integration


def test_fast_golden_regression_against_available_corpus() -> None:
    manifest = GoldenCorpusManifest.default()
    resolved_documents = manifest.resolve_all()
    available = [
        r for r in resolved_documents if r.availability == GoldenDocumentAvailability.AVAILABLE
    ]

    if not available:
        pytest.skip(
            "Golden corpus not provisioned locally under TestDoc/ - "
            "skipping fast regression (see approved decision: the PDF "
            "corpus is externally/local-provisioned, never committed)."
        )

    report = run_fast_golden_regression(manifest=manifest, allow_real_parsing=True)

    writer = GoldenEvaluationReportWriter()
    output_dir = PROJECT_ROOT / "outputs" / "evaluation" / "golden"
    writer.write_json(report, output_dir / "golden_evaluation_report.json")
    writer.write_markdown(report, output_dir / "golden_evaluation_report.md")

    # Every AVAILABLE document must actually have been evaluated - a
    # available-but-unevaluated document (e.g. a parse failure) must fail
    # this test loudly, never be silently absorbed into "corpus evaluated".
    unevaluated_available = [
        outcome
        for outcome in report.document_outcomes
        if outcome.alias in {r.alias for r in available} and not outcome.was_evaluated
    ]
    assert not unevaluated_available, (
        "Available golden documents were not evaluated: "
        f"{[(o.alias, o.status.value, o.detail) for o in unevaluated_available]}"
    )

    structural_failures = [
        outcome
        for outcome in report.document_outcomes
        if outcome.has_structural_failures
    ]
    assert not structural_failures, (
        "Structural/chunk-invariant regressions in the golden corpus: "
        f"{[(o.alias, [a.name for a in o.structural_result.failed_assertions]) for o in structural_failures]}"
    )
