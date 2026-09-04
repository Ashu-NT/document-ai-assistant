from collections import defaultdict

from src.application.workflows.parsing.builders.document_graph.cross_references.pdf_link.pdf_link_cross_reference_linker import (
    PdfLinkLinkingResult,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.reconciliation.cross_reference_reconciliation_result import (
    CrossReferenceReconciliationDiagnostics,
    CrossReferenceReconciliationResult,
)
from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    CrossReferenceEvidence,
    CrossReferenceReconciliationOutcome,
)
from src.shared.ids import IdGenerator, IdPrefix

_Outcome = CrossReferenceReconciliationOutcome
_Status = ChunkCrossReferenceResolutionStatus


class CrossReferenceReconciliationService:
    """Reconciles fuzzy PAGE_REFERENCE/SECTION_REFERENCE candidates against
    native PDF_LINK_REFERENCE candidates for the same source_chunk_id.

    Pure and stateless: takes plain lists, returns a plain result, never
    touches DocumentGraph. Callers (CrossReferencePipeline) are responsible
    for filtering fuzzy input down to location-type candidates first -
    TABLE_REFERENCE/FIGURE_REFERENCE never enter reconciliation at all.

    See outputs/architecture/pdf_link_cross_reference_plan.md for the full
    decision table this implements.
    """

    def __init__(self, *, id_generator: IdGenerator) -> None:
        self.id_generator = id_generator

    def reconcile(
        self,
        *,
        location_type_fuzzy_references: list[ChunkCrossReference],
        native_result: PdfLinkLinkingResult | None,
    ) -> CrossReferenceReconciliationResult:
        native_references = native_result.references if native_result else []

        fuzzy_by_chunk: dict[str, list[ChunkCrossReference]] = defaultdict(list)
        for candidate in location_type_fuzzy_references:
            fuzzy_by_chunk[candidate.source_chunk_id].append(candidate)

        native_by_chunk: dict[str, list[ChunkCrossReference]] = defaultdict(list)
        for candidate in native_references:
            native_by_chunk[candidate.source_chunk_id].append(candidate)

        evidence: list[CrossReferenceEvidence] = []
        canonical_references: list[ChunkCrossReference] = []
        counts = {
            "single_source_count": 0,
            "confirmed_count": 0,
            "accepted_textual_count": 0,
            "accepted_native_count": 0,
            "conflict_count": 0,
            "unreconciled_multi_candidate_chunks": 0,
        }

        for source_chunk_id in set(fuzzy_by_chunk) | set(native_by_chunk):
            fuzzy_candidates = fuzzy_by_chunk.get(source_chunk_id, [])
            # Native candidates are always resolved by construction -
            # PdfLinkCrossReferenceLinker never emits an unresolved/
            # ambiguous ChunkCrossReference, only RESOLVED_UNIQUE ones.
            resolved_native = native_by_chunk.get(source_chunk_id, [])

            unresolved_fuzzy = [
                c for c in fuzzy_candidates if c.target_chunk_id is None
            ]
            resolved_fuzzy = [
                c for c in fuzzy_candidates if c.target_chunk_id is not None
            ]

            for candidate in unresolved_fuzzy:
                evidence.append(
                    self._to_evidence(
                        candidate,
                        outcome=_Outcome.SINGLE_SOURCE,
                        group_id=None,
                        canonical_cross_reference_id=None,
                    )
                )
                counts["single_source_count"] += 1

            if not resolved_fuzzy and not resolved_native:
                continue

            if not resolved_fuzzy or not resolved_native:
                # Only one side has any resolved candidate(s) for this chunk
                # - independent edges, nothing to pair, no ambiguity.
                for candidate in resolved_fuzzy + resolved_native:
                    ev, canonical = self._emit_single_source(candidate)
                    evidence.append(ev)
                    canonical_references.append(canonical)
                    counts["single_source_count"] += 1
                continue

            if len(resolved_fuzzy) == 1 and len(resolved_native) == 1:
                outcome, evs, canonical = self._reconcile_pair(
                    fuzzy_candidate=resolved_fuzzy[0],
                    native_candidate=resolved_native[0],
                )
                evidence.extend(evs)
                if canonical is not None:
                    canonical_references.append(canonical)
                counts[f"{outcome.value}_count"] += 1
                continue

            # Both sides present, but not the clean 1-and-1 case: pairing
            # which fuzzy candidate corresponds to which native candidate is
            # undecidable without bbox/source-location matching. Do not
            # guess - evidence only, no canonical row for anyone here.
            multi_candidate_group_id = self._new_group_id()
            evidence.extend(
                self._to_evidence(
                    candidate,
                    outcome=_Outcome.UNRECONCILED_MULTI_CANDIDATE,
                    group_id=multi_candidate_group_id,
                    canonical_cross_reference_id=None,
                )
                for candidate in resolved_fuzzy + resolved_native
            )
            counts["unreconciled_multi_candidate_chunks"] += 1

        return CrossReferenceReconciliationResult(
            evidence=evidence,
            canonical_references=canonical_references,
            diagnostics=CrossReferenceReconciliationDiagnostics(**counts),
        )

    def _reconcile_pair(
        self,
        *,
        fuzzy_candidate: ChunkCrossReference,
        native_candidate: ChunkCrossReference,
    ) -> tuple[
        CrossReferenceReconciliationOutcome,
        list[CrossReferenceEvidence],
        ChunkCrossReference | None,
    ]:
        if fuzzy_candidate.target_chunk_id == native_candidate.target_chunk_id:
            evs, canonical = self._emit_confirmed(fuzzy_candidate, native_candidate)
            return _Outcome.CONFIRMED, evs, canonical

        is_explicit_section = (
            fuzzy_candidate.reference_type == ChunkCrossReferenceType.SECTION_REFERENCE
            and fuzzy_candidate.resolution_status == _Status.RESOLVED_UNIQUE
        )
        if is_explicit_section:
            evs, canonical = self._emit_accepted(
                fuzzy_candidate,
                native_candidate,
                winner=fuzzy_candidate,
                outcome=_Outcome.ACCEPTED_TEXTUAL,
            )
            return _Outcome.ACCEPTED_TEXTUAL, evs, canonical

        is_unreliable_page_reference = (
            fuzzy_candidate.reference_type == ChunkCrossReferenceType.PAGE_REFERENCE
            and fuzzy_candidate.resolution_status == _Status.RESOLVED_UNIQUE
        )
        if is_unreliable_page_reference:
            # Both sides are nominally "unique," but a page-number citation
            # carries the printed/physical page-offset risk - neither side
            # is trusted over the other. Do not guess.
            evs = self._emit_conflict(fuzzy_candidate, native_candidate)
            return _Outcome.CONFLICT, evs, None

        # Remaining case: fuzzy candidate is weak/heuristic
        # (RESOLVED_AMBIGUOUS, including the section descendant-fallback
        # tier) - a unique native link beats it.
        evs, canonical = self._emit_accepted(
            fuzzy_candidate,
            native_candidate,
            winner=native_candidate,
            outcome=_Outcome.ACCEPTED_NATIVE,
        )
        return _Outcome.ACCEPTED_NATIVE, evs, canonical

    def _emit_single_source(
        self, candidate: ChunkCrossReference
    ) -> tuple[CrossReferenceEvidence, ChunkCrossReference]:
        canonical_id = self.id_generator.new_id(IdPrefix.CROSS_REFERENCE)
        evidence = self._to_evidence(
            candidate,
            outcome=_Outcome.SINGLE_SOURCE,
            group_id=None,
            canonical_cross_reference_id=canonical_id,
        )
        canonical = self._clone_as_canonical(
            candidate,
            cross_reference_id=canonical_id,
            outcome=_Outcome.SINGLE_SOURCE,
        )
        return evidence, canonical

    def _emit_confirmed(
        self,
        fuzzy_candidate: ChunkCrossReference,
        native_candidate: ChunkCrossReference,
    ) -> tuple[list[CrossReferenceEvidence], ChunkCrossReference]:
        group_id = self._new_group_id()
        canonical_id = self.id_generator.new_id(IdPrefix.CROSS_REFERENCE)

        # Deterministic canonical-shape rule (not "always native's shape"):
        # an explicit section/chapter identifier is more informative to a
        # reader than a bare page number, which adds nothing a resolved
        # link doesn't already give you. In both branches link_provenance
        # is attached, since native evidence participated in confirming
        # this edge regardless of which type wins the label.
        base = (
            fuzzy_candidate
            if fuzzy_candidate.reference_type
            == ChunkCrossReferenceType.SECTION_REFERENCE
            else native_candidate
        )
        canonical = self._clone_as_canonical(
            base,
            cross_reference_id=canonical_id,
            outcome=_Outcome.CONFIRMED,
            link_provenance=native_candidate.link_provenance,
        )

        evidence = [
            self._to_evidence(
                fuzzy_candidate,
                outcome=_Outcome.CONFIRMED,
                group_id=group_id,
                canonical_cross_reference_id=canonical_id,
            ),
            self._to_evidence(
                native_candidate,
                outcome=_Outcome.CONFIRMED,
                group_id=group_id,
                canonical_cross_reference_id=canonical_id,
            ),
        ]
        return evidence, canonical

    def _emit_accepted(
        self,
        fuzzy_candidate: ChunkCrossReference,
        native_candidate: ChunkCrossReference,
        *,
        winner: ChunkCrossReference,
        outcome: CrossReferenceReconciliationOutcome,
    ) -> tuple[list[CrossReferenceEvidence], ChunkCrossReference]:
        group_id = self._new_group_id()
        canonical_id = self.id_generator.new_id(IdPrefix.CROSS_REFERENCE)
        canonical = self._clone_as_canonical(
            winner, cross_reference_id=canonical_id, outcome=outcome
        )
        evidence = [
            self._to_evidence(
                fuzzy_candidate,
                outcome=outcome,
                group_id=group_id,
                canonical_cross_reference_id=canonical_id,
            ),
            self._to_evidence(
                native_candidate,
                outcome=outcome,
                group_id=group_id,
                canonical_cross_reference_id=canonical_id,
            ),
        ]
        return evidence, canonical

    def _emit_conflict(
        self,
        fuzzy_candidate: ChunkCrossReference,
        native_candidate: ChunkCrossReference,
    ) -> list[CrossReferenceEvidence]:
        group_id = self._new_group_id()
        return [
            self._to_evidence(
                fuzzy_candidate,
                outcome=_Outcome.CONFLICT,
                group_id=group_id,
                canonical_cross_reference_id=None,
            ),
            self._to_evidence(
                native_candidate,
                outcome=_Outcome.CONFLICT,
                group_id=group_id,
                canonical_cross_reference_id=None,
            ),
        ]

    def _to_evidence(
        self,
        candidate: ChunkCrossReference,
        *,
        outcome: CrossReferenceReconciliationOutcome,
        group_id: str | None,
        canonical_cross_reference_id: str | None,
    ) -> CrossReferenceEvidence:
        return CrossReferenceEvidence(
            evidence_id=self.id_generator.new_id(IdPrefix.CROSS_REFERENCE_EVIDENCE),
            document_id=candidate.document_id,
            source_chunk_id=candidate.source_chunk_id,
            reference_type=candidate.reference_type,
            matched_text=candidate.matched_text,
            target_page=candidate.target_page,
            target_section_label=candidate.target_section_label,
            target_chunk_id=candidate.target_chunk_id,
            resolution_status=candidate.resolution_status,
            confidence_score=candidate.confidence_score,
            link_provenance=candidate.link_provenance,
            reconciliation_outcome=outcome,
            reconciliation_group_id=group_id,
            canonical_cross_reference_id=canonical_cross_reference_id,
        )

    @staticmethod
    def _clone_as_canonical(
        candidate: ChunkCrossReference,
        *,
        cross_reference_id: str,
        outcome: CrossReferenceReconciliationOutcome,
        link_provenance=None,
    ) -> ChunkCrossReference:
        return ChunkCrossReference(
            cross_reference_id=cross_reference_id,
            document_id=candidate.document_id,
            source_chunk_id=candidate.source_chunk_id,
            reference_type=candidate.reference_type,
            matched_text=candidate.matched_text,
            target_page=candidate.target_page,
            target_section_label=candidate.target_section_label,
            target_asset_label=candidate.target_asset_label,
            target_chunk_id=candidate.target_chunk_id,
            resolution_status=candidate.resolution_status,
            confidence_score=candidate.confidence_score,
            link_provenance=(
                link_provenance if link_provenance is not None
                else candidate.link_provenance
            ),
            reconciliation_outcome=outcome,
        )

    def _new_group_id(self) -> str:
        return self.id_generator.new_id(IdPrefix.CROSS_REFERENCE_EVIDENCE)


__all__ = ["CrossReferenceReconciliationService"]
