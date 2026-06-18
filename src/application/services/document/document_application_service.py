from src.application.services.document.document_lookup_service import (
    DocumentLookupService,
)
from src.application.services.document.document_registration_service import (
    DocumentRegistrationService,
)
from src.application.services.document.duplicate_detection_service import (
    DuplicateDetectionService,
)


class DocumentApplicationService:
    def __init__(
        self,
        duplicate_detection: DuplicateDetectionService,
        lookup: DocumentLookupService,
        registration: DocumentRegistrationService,
    ) -> None:
        self.duplicate_detection = duplicate_detection
        self.lookup = lookup
        self.registration = registration