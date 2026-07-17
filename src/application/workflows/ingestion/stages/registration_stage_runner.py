from __future__ import annotations

from collections.abc import Callable

from src.application.services.document import DocumentRegistrationService
from src.shared.activity import ActivityContext


class RegistrationStageRunner:
    def __init__(
        self,
        *,
        document_registration_service: DocumentRegistrationService,
        commit: Callable[[], None],
    ) -> None:
        self.document_registration_service = document_registration_service
        self.commit = commit

    def run(
        self,
        *,
        document_graph,
        replace_existing: bool,
        activity_context: ActivityContext | None = None,
    ) -> None:
        if replace_existing:
            self.document_registration_service.replace_document_graph(
                document_graph,
                activity_context=activity_context,
            )
        else:
            self.document_registration_service.register_document_graph(
                document_graph,
                activity_context=activity_context,
            )
        self.commit()
