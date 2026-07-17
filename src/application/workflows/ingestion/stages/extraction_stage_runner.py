from __future__ import annotations

from collections.abc import Callable

from src.application.services.document import (
    DeterministicIdentifierScanner,
    DocumentRegistrationService,
    IdentifierPromotionService,
)
from src.application.workflows.extraction import ExtractionWorkflow
from src.application.workflows.ingestion.stages.extraction_stage_result import (
    ExtractionStageResult,
)
from src.application.workflows.linking import SemanticLinkingWorkflow
from src.shared.activity import ActivityContext
from src.shared.ids import IdGenerator
from src.shared.progress.progress_emitter import emit_progress


class ExtractionStageRunner:
    def __init__(
        self,
        *,
        extraction_workflow: ExtractionWorkflow,
        document_registration_service: DocumentRegistrationService,
        id_generator: IdGenerator,
        extraction_enabled: bool,
        commit: Callable[[], None],
        identifier_promotion_service: IdentifierPromotionService | None = None,
        deterministic_identifier_scanner: DeterministicIdentifierScanner | None = None,
        semantic_linking_workflow: SemanticLinkingWorkflow | None = None,
    ) -> None:
        self.extraction_workflow = extraction_workflow
        self.document_registration_service = document_registration_service
        self.id_generator = id_generator
        self.extraction_enabled = extraction_enabled
        self.commit = commit
        self.identifier_promotion_service = identifier_promotion_service
        self.deterministic_identifier_scanner = deterministic_identifier_scanner
        self.semantic_linking_workflow = semantic_linking_workflow

    def run(
        self,
        *,
        final_graph,
        replace_existing: bool,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> ExtractionStageResult:
        extraction_result = None
        scanned_identifier_count = 0
        semantic_relationship_count = None
        if self.extraction_enabled:
            extraction_result = self.extraction_workflow.extract(
                final_graph.document.document_id,
                list(final_graph.chunks.values()),
                activity_context=activity_context,
                progress_callback=progress_callback,
                replace_existing=replace_existing,
                tables=final_graph.tables,
                sections=final_graph.sections,
            )
            self.commit()
            self._promote_identifiers_if_available(
                extraction_result=extraction_result,
                final_graph=final_graph,
                activity_context=activity_context,
            )
        else:
            emit_progress(progress_callback, self._skip_message())

        scanned_identifier_count = self._scan_identifiers_if_available(
            final_graph=final_graph,
            activity_context=activity_context,
        )
        if self.semantic_linking_workflow is not None:
            relationships = self.semantic_linking_workflow.link(
                final_graph.document.document_id
            )
            semantic_relationship_count = len(relationships)
            self.commit()
        return ExtractionStageResult(
            extraction_result=extraction_result,
            deterministic_identifier_count=scanned_identifier_count,
            semantic_relationship_count=semantic_relationship_count,
        )

    def _promote_identifiers_if_available(
        self,
        *,
        extraction_result,
        final_graph,
        activity_context: ActivityContext | None,
    ) -> None:
        if self.identifier_promotion_service is None:
            return
        promoted_identifiers = self.identifier_promotion_service.promote(
            extraction_result=extraction_result,
            document_graph=final_graph,
            id_generator=self.id_generator,
        )
        if not promoted_identifiers:
            return
        for identifier in promoted_identifiers:
            final_graph.identifiers[identifier.identifier_id] = identifier
        self.document_registration_service.register_document_identifiers(
            promoted_identifiers,
            activity_context=activity_context,
        )
        self.commit()

    def _scan_identifiers_if_available(
        self,
        *,
        final_graph,
        activity_context: ActivityContext | None,
    ) -> int:
        if self.deterministic_identifier_scanner is None:
            return 0
        existing_normalized = {
            (identifier.normalized_value or "", identifier.identifier_type.value)
            for identifier in final_graph.identifiers.values()
        }
        scanned_identifiers = self.deterministic_identifier_scanner.scan(
            final_graph,
            self.id_generator,
            existing_normalized=existing_normalized,
        )
        if not scanned_identifiers:
            return 0
        for identifier in scanned_identifiers:
            final_graph.identifiers[identifier.identifier_id] = identifier
        self.document_registration_service.register_document_identifiers(
            scanned_identifiers,
            activity_context=activity_context,
        )
        self.commit()
        return len(scanned_identifiers)

    def _skip_message(self) -> str:
        if self.deterministic_identifier_scanner is not None:
            return (
                "Extraction skipped by config. Running deterministic "
                "identifier scan only."
            )
        return "Extraction skipped by config."
