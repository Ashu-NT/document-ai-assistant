from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class StructuralBaselineProvenance:
    """The parsing environment a structural expectation baseline was
    reviewed/recorded under - optional, informational only.

    Every field is `None` unless a fixture author explicitly recorded it;
    absence means "not recorded", never a fabricated/guessed value (see
    outputs/architecture/upstream_structural_quality_investigation.md Part D
    - the FWC12 baseline's own provenance turned out to be unrecoverable
    precisely because nothing like this existed when it was authored).

    Never used to automatically invalidate or fail a baseline - a
    provenance mismatch against the current run's real parser/version is
    reported diagnostically (see GoldenEvaluationReportMarkdownRenderer),
    never turned into a new failing assertion.
    """

    parser_name: str | None = None
    parser_version: str | None = None
    conversion_fingerprint: str | None = None

    @property
    def is_recorded(self) -> bool:
        return (
            self.parser_name is not None
            or self.parser_version is not None
            or self.conversion_fingerprint is not None
        )


__all__ = ["StructuralBaselineProvenance"]
